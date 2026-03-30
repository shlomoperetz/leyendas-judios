#!/usr/bin/env python3
"""
Pipeline de traducción: Las Leyendas de los Judíos (Louis Ginzberg)
Inglés → Español usando dos agentes Claude.

Uso:
  python pipeline.py                 # Pipeline completo
  python pipeline.py --solo-parsear  # Solo muestra secciones detectadas (sin traducir)
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import anthropic
import requests

# ─── Configuración ────────────────────────────────────────────────────────────

MODEL_TRADUCTOR = "claude-opus-4-6"
MODEL_REVISOR = "claude-sonnet-4-6"
CHECKPOINT_FILE = Path("checkpoint.json")
OUTPUT_DIR = Path("output/vol1")
FUENTES_DIR = Path("fuentes")
VOL1_FILE = FUENTES_DIR / "vol1.txt"
PAUSA_ENTRE_LLAMADAS = 3  # segundos entre llamadas a la API

# ─── System prompts ───────────────────────────────────────────────────────────

TRADUCTOR_SYSTEM = (
    "Eres un escritor español de alto nivel traduciendo una obra narrativa épica "
    "sobre la historia del pueblo judío según la tradición rabínica. El estilo debe "
    "ser culto, fluido, con cadencia bíblica pero sin rigidez litúrgica. No es "
    "traducción sagrada sino literatura. Usa \"el Eterno\" para God/Lord/the Lord. "
    "Preserva los nombres propios en su forma hebrea (Moshé, Noaj, Avraham, "
    "Itzjak, Yaakov). Los términos hebreos específicos (Shejiná, Torá, mitzvá, "
    "etc.) se preservan en español sin traducir. No añadas notas al pie en el "
    "cuerpo del texto."
)

REVISOR_SYSTEM = (
    "Eres un revisor literario. Recibes el texto original en inglés y la "
    "traducción al español. Tu tarea: verificar fidelidad narrativa al original, "
    "coherencia terminológica con el resto del texto, y que el español fluya como "
    "literatura, no como traducción. Si la traducción es buena, devuélvela tal "
    "cual. Si hay problemas, corrígelos y devuelve la versión mejorada. "
    "Devuelve SOLO el texto corregido, sin comentarios ni explicaciones."
)


# ─── Descarga ─────────────────────────────────────────────────────────────────

def buscar_url_gutenberg():
    """Localiza el Volumen I de Ginzberg via Gutendex y devuelve la URL del .txt."""
    print("Buscando en Gutendex...")
    resp = requests.get(
        "https://gutendex.com/books/",
        params={"search": "Legends of the Jews Ginzberg"},
        timeout=30,
    )
    resp.raise_for_status()
    resultados = resp.json().get("results", [])

    # Intentar encontrar específicamente el Vol. I
    for libro in resultados:
        titulo = libro.get("title", "").lower()
        es_volumen_uno = any(
            t in titulo for t in ["volume i", "vol. i", "vol i", "volume 1", "vol. 1"]
        )
        if "legends of the jews" in titulo and es_volumen_uno:
            formats = libro.get("formats", {})
            url = (
                formats.get("text/plain; charset=utf-8")
                or formats.get("text/plain; charset=us-ascii")
                or formats.get("text/plain")
            )
            if url:
                print(f"  Encontrado: {libro['title']} (ID {libro['id']})")
                return url

    # Fallback: primer resultado con título "Legends of the Jews" y texto plano
    for libro in resultados:
        titulo = libro.get("title", "").lower()
        if "legends of the jews" in titulo:
            formats = libro.get("formats", {})
            url = (
                formats.get("text/plain; charset=utf-8")
                or formats.get("text/plain; charset=us-ascii")
                or formats.get("text/plain")
            )
            if url:
                print(f"  Usando como fallback: {libro['title']} (ID {libro['id']})")
                return url

    raise ValueError(
        "No se encontró el texto en Gutendex. "
        "Descárgalo manualmente en https://www.gutenberg.org y guárdalo en fuentes/vol1.txt"
    )


def descargar_vol1():
    """Descarga el Vol. I si no existe ya en fuentes/."""
    FUENTES_DIR.mkdir(parents=True, exist_ok=True)

    if VOL1_FILE.exists():
        print(f"Texto ya descargado: {VOL1_FILE} ({VOL1_FILE.stat().st_size:,} bytes)")
        return

    url = buscar_url_gutenberg()
    print(f"Descargando desde {url} ...")
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    VOL1_FILE.write_bytes(resp.content)
    print(f"Guardado en {VOL1_FILE} ({VOL1_FILE.stat().st_size:,} bytes)")


# ─── Parser ───────────────────────────────────────────────────────────────────

def strip_gutenberg_boilerplate(texto):
    """Elimina el encabezado y pie de página de Project Gutenberg."""
    # Inicio del texto real
    m_inicio = re.search(
        r"\*\*\*\s*START OF (THIS |THE )?PROJECT GUTENBERG EBOOK[^\*]*\*\*\*",
        texto, re.IGNORECASE,
    )
    if m_inicio:
        texto = texto[m_inicio.end():]

    # Fin del texto real
    m_fin = re.search(
        r"\*\*\*\s*END OF (THIS |THE )?PROJECT GUTENBERG EBOOK",
        texto, re.IGNORECASE,
    )
    if m_fin:
        texto = texto[: m_fin.start()]

    return texto


def limpiar_notas_al_pie(texto):
    """
    Elimina marcadores numéricos de notas al pie ([1], [2], etc.)
    y bloques de notas al pie al final de las secciones.
    """
    # Marcadores inline: [1], [23], etc.
    texto = re.sub(r'\[\d+\]', '', texto)
    return texto


def es_encabezado(linea):
    """
    Decide si una línea es un encabezado de sección.
    Criterios: no vacía, en MAYÚSCULAS, longitud razonable,
    no es una línea de separación ni metadata de Gutenberg.
    """
    stripped = linea.strip()
    if len(stripped) < 3:
        return False
    # Líneas demasiado largas no son encabezados
    if len(stripped) > 100:
        return False
    # Líneas de separación (guiones, asteriscos, etc.)
    if re.fullmatch(r'[\-\*\=\_\s\~]+', stripped):
        return False
    # Líneas de numeración romana sola (I, II, III, ...) sí son encabezados
    if re.fullmatch(r'[IVXLCDM]+\.?', stripped):
        return True
    # Metadata de Gutenberg
    if any(kw in stripped.lower() for kw in ['gutenberg', 'www.', 'http', 'ebook']):
        return False
    # Calcular ratio de letras en mayúsculas
    letras = [c for c in stripped if c.isalpha()]
    if not letras:
        return False
    ratio_mayus = sum(1 for c in letras if c.isupper()) / len(letras)
    return ratio_mayus >= 0.75


def parsear_secciones(texto):
    """
    Divide el texto en secciones. Devuelve lista de dicts:
      [{'titulo': str, 'cuerpo': str}, ...]
    """
    texto = strip_gutenberg_boilerplate(texto)
    texto = limpiar_notas_al_pie(texto)

    lineas = texto.split('\n')
    secciones = []
    titulo_actual = None
    cuerpo_lineas = []

    for linea in lineas:
        if es_encabezado(linea):
            # Guardar sección anterior
            if titulo_actual is not None:
                cuerpo = '\n'.join(cuerpo_lineas).strip()
                if cuerpo:
                    secciones.append({'titulo': titulo_actual, 'cuerpo': cuerpo})
            titulo_actual = linea.strip()
            cuerpo_lineas = []
        else:
            cuerpo_lineas.append(linea)

    # Última sección
    if titulo_actual is not None:
        cuerpo = '\n'.join(cuerpo_lineas).strip()
        if cuerpo:
            secciones.append({'titulo': titulo_actual, 'cuerpo': cuerpo})

    return secciones


# ─── Agentes ──────────────────────────────────────────────────────────────────

def traducir_seccion(client, titulo, cuerpo):
    """
    Agente 1 — Traductor literario.
    Devuelve el texto traducido al español.
    """
    prompt = (
        f'Traduce al español la siguiente sección de "Las Leyendas de los Judíos" '
        f'de Louis Ginzberg.\n\n'
        f'TÍTULO: {titulo}\n\n'
        f'TEXTO ORIGINAL:\n{cuerpo}\n\n'
        f'Devuelve SOLO el texto traducido, sin repetir el título ni añadir comentarios.'
    )
    with client.messages.stream(
        model=MODEL_TRADUCTOR,
        max_tokens=8000,
        system=TRADUCTOR_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        return stream.get_final_message().content[0].text.strip()


def revisar_traduccion(client, titulo, cuerpo_original, cuerpo_traducido):
    """
    Agente 2 — Revisor literario.
    Devuelve la traducción corregida (o la misma si está bien).
    """
    prompt = (
        f'Revisa esta traducción de "Las Leyendas de los Judíos".\n\n'
        f'TÍTULO: {titulo}\n\n'
        f'ORIGINAL (inglés):\n{cuerpo_original}\n\n'
        f'TRADUCCIÓN (español):\n{cuerpo_traducido}'
    )
    with client.messages.stream(
        model=MODEL_REVISOR,
        max_tokens=8000,
        system=REVISOR_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        return stream.get_final_message().content[0].text.strip()


# ─── Checkpoint ───────────────────────────────────────────────────────────────

def cargar_checkpoint():
    if CHECKPOINT_FILE.exists():
        return json.loads(CHECKPOINT_FILE.read_text(encoding="utf-8"))
    return {"completadas": []}


def guardar_checkpoint(checkpoint):
    CHECKPOINT_FILE.write_text(
        json.dumps(checkpoint, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ─── Output ───────────────────────────────────────────────────────────────────

def slug_titulo(titulo):
    """Convierte un título en un slug apto para nombre de archivo."""
    s = titulo.lower()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s).strip('-')
    return s[:60]


def ruta_seccion(indice, titulo):
    return OUTPUT_DIR / f"seccion-{indice:03d}-{slug_titulo(titulo)}.md"


def guardar_md(indice, titulo, cuerpo_traducido):
    """Escribe el archivo Markdown de la sección traducida."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ruta = ruta_seccion(indice, titulo)
    ruta.write_text(f"# {titulo}\n\n{cuerpo_traducido}\n", encoding="utf-8")
    return ruta


# ─── Git ──────────────────────────────────────────────────────────────────────

def git_commit_push(titulo, ruta_md):
    """Hace commit del MD y el checkpoint, luego push."""
    subprocess.run(["git", "add", str(ruta_md), str(CHECKPOINT_FILE)], check=True)
    subprocess.run(["git", "commit", "-m", f"traduce: {titulo}"], check=True)
    subprocess.run(["git", "push"], check=True)


# ─── Comandos ─────────────────────────────────────────────────────────────────

def cmd_solo_parsear():
    """Descarga el texto, detecta secciones y las muestra por pantalla."""
    descargar_vol1()
    texto = VOL1_FILE.read_text(encoding="utf-8", errors="replace")
    secciones = parsear_secciones(texto)

    sep = "─" * 70
    print(f"\n{sep}")
    print(f"  {len(secciones)} secciones detectadas en {VOL1_FILE}")
    print(f"{sep}\n")
    for i, s in enumerate(secciones, 1):
        palabras = len(s['cuerpo'].split())
        print(f"  [{i:3d}] {s['titulo'][:65]:<65} ({palabras:>6,} palabras)")
    print()


def cmd_pipeline():
    """Ejecuta el pipeline completo de descarga → parse → traducción → commit."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: La variable ANTHROPIC_API_KEY no está definida.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # 1. Descargar texto
    descargar_vol1()

    # 2. Parsear secciones
    texto = VOL1_FILE.read_text(encoding="utf-8", errors="replace")
    secciones = parsear_secciones(texto)
    print(f"\n{len(secciones)} secciones detectadas.\n")

    # 3. Cargar checkpoint
    checkpoint = cargar_checkpoint()
    completadas = set(checkpoint.get("completadas", []))

    pendientes = [(i, s) for i, s in enumerate(secciones, 1) if str(i) not in completadas]
    ya_hechas = len(secciones) - len(pendientes)
    if ya_hechas:
        print(f"  ({ya_hechas} ya traducidas, continuando desde donde quedó)\n")
    print(f"{len(pendientes)} secciones pendientes.\n")

    # 4. Traducir
    for i, seccion in pendientes:
        titulo = seccion['titulo']
        cuerpo = seccion['cuerpo']

        print(f"[{i}/{len(secciones)}] {titulo[:65]}")
        print(f"  → Agente 1: traduciendo...")

        try:
            traduccion = traducir_seccion(client, titulo, cuerpo)
        except anthropic.RateLimitError as e:
            retry = int(getattr(e.response, 'headers', {}).get('retry-after', 60))
            print(f"  Rate limit. Esperando {retry}s...")
            time.sleep(retry)
            traduccion = traducir_seccion(client, titulo, cuerpo)

        time.sleep(PAUSA_ENTRE_LLAMADAS)
        print(f"  → Agente 2: revisando...")

        try:
            traduccion_final = revisar_traduccion(client, titulo, cuerpo, traduccion)
        except anthropic.RateLimitError as e:
            retry = int(getattr(e.response, 'headers', {}).get('retry-after', 60))
            print(f"  Rate limit. Esperando {retry}s...")
            time.sleep(retry)
            traduccion_final = revisar_traduccion(client, titulo, cuerpo, traduccion)

        time.sleep(PAUSA_ENTRE_LLAMADAS)

        # Guardar MD
        ruta_md = guardar_md(i, titulo, traduccion_final)
        print(f"  ✓ {ruta_md}")

        # Actualizar checkpoint
        completadas.add(str(i))
        checkpoint["completadas"] = sorted(completadas, key=lambda x: int(x))
        guardar_checkpoint(checkpoint)

        # Commit + push
        try:
            git_commit_push(titulo, ruta_md)
            print(f"  ✓ Commit y push realizados\n")
        except subprocess.CalledProcessError as e:
            print(f"  ⚠ Error en git: {e} (continuando...)\n")

    print("=" * 60)
    print("Pipeline completado.")
    print(f"Archivos en {OUTPUT_DIR}/")


# ─── Entrada ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--solo-parsear" in sys.argv:
        cmd_solo_parsear()
    else:
        cmd_pipeline()
