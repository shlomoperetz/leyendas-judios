#!/usr/bin/env python3
"""
Corrección editorial en bloque - Volumen I
Las Leyendas de los Judíos · Editorial Sefardí
Basado en la auditoría de fallos a rectificar.
"""

import os
import re

VOL1 = "/home/adamshlomo/leyendas-judios/output/vol1"

def apply_corrections(text):

    # ══════════════════════════════════════════════
    # 1. CALCOS LITERARIOS (antes de reemplazos genéricos)
    # ══════════════════════════════════════════════

    # #8 — vida práctica y palpitante
    text = text.replace(
        "producto de la vida práctica y palpitante",
        "fruto de una vida práctica y viva"
    )
    text = text.replace("vida práctica y palpitante", "vida práctica y viva")

    # #7 — tomó consejo con la Torá
    text = text.replace("tomó consejo con la Torá", "consultó a la Torá")

    # #9 — Estos intentaban aprehender y modelar
    text = text.replace(
        "cotidiana. Estos intentaban aprehender y modelar.",
        "cotidiana, que procuraban comprender y ordenar."
    )
    text = text.replace(
        "Estos intentaban aprehender y modelar",
        "que procuraban comprender y ordenar"
    )

    # #10 — en prosecución de mi propósito
    text = text.replace(
        "en prosecución de mi propósito de ofrecer una presentación fluida",
        "con el fin de ofrecer una presentación fluida"
    )

    # #11 — el todo seguía aún en peligro
    text = text.replace(
        "el todo seguía aún en peligro de destrucción",
        "todo seguía en peligro de destrucción"
    )

    # #12 — lugar inquietante
    text = text.replace("lugar inquietante", "lugar temible")

    # #13 — las partes de estas personas dobles
    text = text.replace(
        "las partes de estas personas dobles riñen entre sí",
        "las dos mitades de estos seres riñen entre sí"
    )

    # #14 — Fue hecho cristalizar
    text = text.replace(
        "Fue hecho cristalizar hasta adquirir su solidez",
        "se cristalizó hasta adquirir solidez"
    )
    text = text.replace("Fue hecho cristalizar", "se cristalizó")

    # Título del índice: "El niño proclama a Dios" → "El niño reconoce al Eterno"
    text = text.replace("El niño proclama a Dios", "El niño reconoce al Eterno")
    text = text.replace("el niño proclama a Dios", "el niño reconoce al Eterno")

    # ══════════════════════════════════════════════
    # 4. MESÍAS → MASHÍAJ
    # ══════════════════════════════════════════════

    text = text.replace("del Mesías", "del Mashíaj")
    text = text.replace("al Mesías", "al Mashíaj")
    text = text.replace("el Mesías", "el Mashíaj")
    text = text.replace("El Mesías", "El Mashíaj")
    text = re.sub(r'\bMesías\b', 'Mashíaj', text)

    # ══════════════════════════════════════════════
    # 5. INFIERNO / infierno → GUEHINOM
    # ══════════════════════════════════════════════

    for prefix in ["del ", "al ", "el ", "El ", "Del ", "Al "]:
        for variant in ["infierno", "Infierno"]:
            text = text.replace(prefix + variant, prefix + "Guehinom")

    text = re.sub(r'\b[Ii]nfierno\b', 'Guehinom', text)

    # ══════════════════════════════════════════════
    # 2. SEÑOR → EL ETERNO
    # (excepto locuciones rabínicas fijas)
    # ══════════════════════════════════════════════

    # Proteger locuciones fijas
    senor_prot = [
        ("Señor del mundo",           "__SDMUNDO__"),
        ("Señor del universo",         "__SDUNIV__"),
        ("Señor menor",                "__SMENOR__"),
        ("Señor de señores",           "__SDESEJ__"),
        ("Señor de todos los señores", "__SDTSL__"),
    ]
    for orig, tok in senor_prot:
        text = text.replace(orig, tok)

    # Reemplazos específicos
    text = text.replace("del Señor", "del Eterno")
    text = text.replace("al Señor",  "al Eterno")
    text = text.replace("El Señor",  "El Eterno")
    text = text.replace("el Señor",  "el Eterno")
    text = text.replace("Oh Señor",  "Oh, Eterno")
    text = text.replace("Oh, Señor", "Oh, Eterno")
    text = text.replace("oh Señor",  "oh, Eterno")
    text = text.replace("Señor mío",    "Eterno mío")
    text = text.replace("Señor nuestro","Eterno nuestro")

    # Inicio de oración
    text = re.sub(r'(?<=[.!?»\u00bb] )Señor\b', 'El Eterno', text)
    text = re.sub(r'^Señor\b', 'El Eterno', text, flags=re.MULTILINE)

    # Cualquier Señor restante
    text = re.sub(r'\bSeñor\b', 'el Eterno', text)

    # Restaurar protegidos
    for orig, tok in senor_prot:
        text = text.replace(tok, orig)

    # ══════════════════════════════════════════════
    # 1. DIOS → EL ETERNO
    # ══════════════════════════════════════════════

    # Proteger formas posesivas (Elohim compuesto: YHWH + Elohim)
    dios_prot = [
        ("vuestro Dios",  "__VDIOS__"),
        ("Vuestro Dios",  "__VDIOS2__"),
        ("tu Dios",       "__TDIOS__"),
        ("Tu Dios",       "__TDIOS2__"),
        ("mi Dios",       "__MDIOS__"),
        ("Mi Dios",       "__MDIOS2__"),
        ("su Dios",       "__SUDIOS__"),
        ("Su Dios",       "__SUDIOS2__"),
        ("nuestro Dios",  "__NDIOS__"),
        ("Nuestro Dios",  "__NDIOS2__"),
        ("El Dios de",    "__EDDIOS__"),
        ("el Dios de",    "__eddios__"),
        ("El Dios vivo",  "__EDVIVO__"),
        ("el Dios vivo",  "__edvivo__"),
    ]
    for orig, tok in dios_prot:
        text = text.replace(orig, tok)

    # Contracciones
    text = text.replace("de Dios", "del Eterno")
    text = text.replace("a Dios",  "al Eterno")

    # Inicio de oración
    text = re.sub(r'(?<=[.!?»\u00bb] )Dios\b', 'El Eterno', text)
    text = re.sub(r'^Dios\b', 'El Eterno', text, flags=re.MULTILINE)

    # Cualquier Dios restante (medio de oración)
    text = re.sub(r'\bDios\b', 'el Eterno', text)

    # Restaurar protegidos
    for orig, tok in dios_prot:
        text = text.replace(tok, orig)

    # Reparar contracciones dobles que pudieran haber quedado
    text = text.replace("del el Eterno", "del Eterno")
    text = text.replace("al el Eterno",  "al Eterno")
    text = text.replace("Del el Eterno", "Del Eterno")

    return text


# ── Procesar todos los archivos ──────────────────
changed = 0
for fname in sorted(os.listdir(VOL1)):
    if not fname.endswith(".md"):
        continue
    fpath = os.path.join(VOL1, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        original = f.read()
    corrected = apply_corrections(original)
    if corrected != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(corrected)
        changed += 1
        print(f"  ✓ {fname}")

print(f"\nTotal archivos modificados: {changed} de 121")
