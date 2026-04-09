#!/usr/bin/env python3
"""
Normalización editorial - Volumen II
Las Leyendas de los Judíos · Editorial Sefardí
"""

import os
import re

VOL2 = "/home/adamshlomo/leyendas-judios/output/vol2"

def apply_corrections(text):

    # ══════════════════════════════════════════════
    # 1. NOMBRES PROPIOS
    # ══════════════════════════════════════════════

    # Job → Iyov
    text = text.replace("Job", "Iyov")

    # José → Yosef
    text = re.sub(r'\bJosé\b', 'Yosef', text)

    # Gabriel → Gavriel
    text = re.sub(r'\bGabriel\b', 'Gavriel', text)

    # Jacob → Yaakov
    text = re.sub(r'\bJacob\b', 'Yaakov', text)

    # Abraham / Isaac en narración ordinaria
    text = re.sub(r'\bAbraham\b', 'Avraham', text)
    text = re.sub(r'\bIsaac\b', 'Itzjak', text)

    # ══════════════════════════════════════════════
    # 2. ARTEFACTOS MECÁNICOS
    # ══════════════════════════════════════════════

    # "hacial Eterno" → "hacia el Eterno"
    text = text.replace("hacial Eterno", "hacia el Eterno")

    # "un el Eterno" → "un Eterno"
    text = re.sub(r'\bun el Eterno\b', 'un Eterno', text)

    # "Oh, Eterno" → "Oh Eterno"
    text = re.sub(r'Oh,\s+Eterno\b', 'Oh Eterno', text)

    # Dobles espacios
    text = re.sub(r'  +', ' ', text)

    # ══════════════════════════════════════════════
    # 3. DIOS → EL ETERNO (con protecciones)
    # ══════════════════════════════════════════════

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

    text = text.replace("de Dios", "del Eterno")
    text = text.replace("a Dios",  "al Eterno")
    text = re.sub(r'(?<=[.!?»\u00bb] )Dios\b', 'El Eterno', text)
    text = re.sub(r'^Dios\b', 'El Eterno', text, flags=re.MULTILINE)
    text = re.sub(r'\bDios\b', 'el Eterno', text)

    for orig, tok in dios_prot:
        text = text.replace(tok, orig)

    # Reparar contracciones dobles
    text = text.replace("del el Eterno", "del Eterno")
    text = text.replace("al el Eterno",  "al Eterno")
    text = text.replace("Del el Eterno", "Del Eterno")
    text = re.sub(r'\bun el Eterno\b', 'un Eterno', text)

    # ══════════════════════════════════════════════
    # 4. SEÑOR → EL ETERNO (con protecciones)
    # ══════════════════════════════════════════════

    senor_prot = [
        ("Señor del mundo entero",         "__SDMUNDOENTERO__"),
        ("Señor del mundo",                "__SDMUNDO__"),
        ("Señor del universo",             "__SDUNIV__"),
        ("Señor menor",                    "__SMENOR__"),
        ("Señor de señores",               "__SDESEJ__"),
        ("Señor de todos los señores",     "__SDTSL__"),
    ]
    for orig, tok in senor_prot:
        text = text.replace(orig, tok)

    text = text.replace("del Señor", "del Eterno")
    text = text.replace("al Señor",  "al Eterno")
    text = text.replace("El Señor",  "El Eterno")
    text = text.replace("el Señor",  "el Eterno")
    text = text.replace("Oh Señor",  "Oh Eterno")
    text = text.replace("Oh, Señor", "Oh Eterno")
    text = text.replace("oh Señor",  "oh Eterno")
    text = text.replace("Señor mío",    "Eterno mío")
    text = text.replace("Señor nuestro","Eterno nuestro")
    text = re.sub(r'(?<=[.!?»\u00bb] )Señor\b', 'El Eterno', text)
    text = re.sub(r'^Señor\b', 'El Eterno', text, flags=re.MULTILINE)
    text = re.sub(r'\bSeñor\b', 'el Eterno', text)

    for orig, tok in senor_prot:
        text = text.replace(tok, orig)

    # ══════════════════════════════════════════════
    # 5. INFIERNO → GUEHINOM
    # ══════════════════════════════════════════════

    text = re.sub(r'\b[Ii]nfierno\b', 'Guehinom', text)

    # ══════════════════════════════════════════════
    # 6. MESÍAS → MASHÍAJ
    # ══════════════════════════════════════════════

    text = re.sub(r'\bMesías\b', 'Mashíaj', text)

    # ══════════════════════════════════════════════
    # 7. MINÚSCULAS TRAS PUNTO
    # ══════════════════════════════════════════════

    text = re.sub(r'\. ([a-záéíóúüñ])', lambda m: '. ' + m.group(1).upper(), text)

    return text


# ── Procesar todos los archivos ──────────────────
changed = 0
for fname in sorted(os.listdir(VOL2)):
    if not fname.endswith(".md"):
        continue
    fpath = os.path.join(VOL2, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        original = f.read()
    corrected = apply_corrections(original)
    if corrected != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(corrected)
        changed += 1
        print(f"  ✓ {fname}")

print(f"\nTotal archivos modificados: {changed} de 95")
