#!/usr/bin/env python3
"""
Normalización editorial - Volumen IV
Las Leyendas de los Judíos · Editorial Sefardí
"""

import os
import re

VOL4 = "/home/adamshlomo/leyendas-judios/output/vol4"

def apply_corrections(text):

    # ══════════════════════════════════════════════
    # 1. NOMBRES PROPIOS
    # ══════════════════════════════════════════════

    text = re.sub(r'\bSamuel\b', 'Shmuel', text)
    text = re.sub(r'\bSalomón\b', 'Shlomó', text)
    text = re.sub(r'\bElías\b', 'Eliyahu', text)
    text = re.sub(r'\bJosué\b', 'Yehoshúa', text)
    text = re.sub(r'\bMoisés\b', 'Moshé', text)

    # ══════════════════════════════════════════════
    # 2. ARTEFACTOS MECÁNICOS
    # ══════════════════════════════════════════════

    # Palabras pegadas con "el Eterno"
    text = text.replace("hacial Eterno", "hacia el Eterno")
    text = text.replace("contral Eterno", "contra el Eterno")
    text = text.replace("seal Eterno", "sea el Eterno")
    text = text.replace("obral Eterno", "obra el Eterno")
    text = text.replace("ahoral Eterno", "ahora el Eterno")

    # "oh el Eterno" → "oh Eterno"
    text = re.sub(r'oh el Eterno\b', 'oh Eterno', text)
    text = re.sub(r'Oh el Eterno\b', 'Oh Eterno', text)
    # "Oh, Eterno" → "Oh Eterno"
    text = re.sub(r'Oh,\s+Eterno\b', 'Oh Eterno', text)

    # "su el Eterno" / "mi el Eterno" / "tu el Eterno" → drop "el"
    text = text.replace("su el Eterno", "su Eterno")
    text = text.replace("mi el Eterno", "mi Eterno")
    text = text.replace("tu el Eterno", "tu Eterno")
    text = text.replace("ese el Eterno", "ese Eterno")

    # "un el Eterno" → "un Eterno"
    text = re.sub(r'\bun el Eterno\b', 'un Eterno', text)

    # "el Eterno el Eterno" → "el Eterno"
    text = re.sub(r'\bel Eterno el Eterno\b', 'el Eterno', text)

    # "cual Eterno" → "cual el Eterno"
    for prefix in ["lo cual ", "la cual ", "del cual ", "a lo cual ", "ante lo cual ",
                   "por lo cual ", "por la cual ", "en la cual ", "mediante la cual ",
                   "por medio del cual ", "tras lo cual "]:
        text = text.replace(prefix + "Eterno", prefix + "el Eterno")

    # del el / al el
    text = text.replace("del el Eterno", "del Eterno")
    text = text.replace("al el Eterno",  "al Eterno")

    # dobles espacios
    text = re.sub(r'  +', ' ', text)

    # ══════════════════════════════════════════════
    # 3. OTROS TÉRMINOS
    # ══════════════════════════════════════════════

    # "conversa piadosa" → "prosélita piadosa"
    text = text.replace("conversa piadosa", "prosélita piadosa")

    # "los cabezas" → "los jefes"
    text = text.replace("los cabezas", "los jefes")

    # Mesías → Mashíaj
    text = re.sub(r'\bMesías\b', 'Mashíaj', text)

    # Infierno → Guehinom
    text = re.sub(r'\b[Ii]nfierno\b', 'Guehinom', text)

    # ══════════════════════════════════════════════
    # 4. MINÚSCULAS TRAS PUNTO
    # ══════════════════════════════════════════════

    text = re.sub(r'\. ([a-záéíóúüñ])', lambda m: '. ' + m.group(1).upper(), text)

    return text


changed = 0
for fname in sorted(os.listdir(VOL4)):
    if not fname.endswith(".md"):
        continue
    fpath = os.path.join(VOL4, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        original = f.read()
    corrected = apply_corrections(original)
    if corrected != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(corrected)
        changed += 1
        print(f"  ✓ {fname}")

print(f"\nTotal archivos modificados: {changed} de 134")
