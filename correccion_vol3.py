#!/usr/bin/env python3
"""
Normalización editorial - Volumen III
Las Leyendas de los Judíos · Editorial Sefardí
"""

import os
import re

VOL3 = "/home/adamshlomo/leyendas-judios/output/vol3"

def apply_corrections(text):

    # ══════════════════════════════════════════════
    # 1. ARTEFACTOS MECÁNICOS
    # ══════════════════════════════════════════════

    # "seal Eterno" → "sea el Eterno"
    text = text.replace("seal Eterno", "sea el Eterno")

    # "contral Eterno" → "contra el Eterno"
    text = text.replace("contral Eterno", "contra el Eterno")

    # "hacial Eterno" → "hacia el Eterno"
    text = text.replace("hacial Eterno", "hacia el Eterno")

    # "siquieral Eterno" → "siquiera el Eterno"
    text = text.replace("siquieral Eterno", "siquiera el Eterno")

    # "en el el Eterno" → "en el Eterno"
    text = text.replace("en el el Eterno", "en el Eterno")

    # "del el Eterno" / "al el Eterno" / "un el Eterno"
    text = text.replace("del el Eterno", "del Eterno")
    text = text.replace("al el Eterno",  "al Eterno")
    text = text.replace("Del el Eterno", "Del Eterno")
    text = re.sub(r'\bun el Eterno\b', 'un Eterno', text)

    # "Oh, Eterno" → "Oh Eterno"
    text = re.sub(r'Oh,\s+Eterno\b', 'Oh Eterno', text)

    # Dobles espacios
    text = re.sub(r'  +', ' ', text)

    # ══════════════════════════════════════════════
    # 2. NOMBRES PROPIOS
    # ══════════════════════════════════════════════

    # Aarón → Aharón
    text = re.sub(r'\bAarón\b', 'Aharón', text)

    # Gabriel → Gavriel
    text = re.sub(r'\bGabriel\b', 'Gavriel', text)

    # Miguel → Mijael (only as angelic name, not as personal name in other contexts)
    text = re.sub(r'\bMiguel\b', 'Mijael', text)

    # Josué → Yehoshúa
    text = re.sub(r'\bJosué\b', 'Yehoshúa', text)

    # Balaam → Bilam
    text = re.sub(r'\bBalaam\b', 'Bilam', text)

    # Mesías → Mashíaj
    text = re.sub(r'\bMesías\b', 'Mashíaj', text)

    # Infierno → Guehinom
    text = re.sub(r'\b[Ii]nfierno\b', 'Guehinom', text)

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

    # Reparar contracciones dobles que pudieran quedar
    text = text.replace("del el Eterno", "del Eterno")
    text = text.replace("al el Eterno",  "al Eterno")
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
    text = text.replace("Señor mío",    "Eterno mío")
    text = text.replace("Señor nuestro","Eterno nuestro")
    text = re.sub(r'(?<=[.!?»\u00bb] )Señor\b', 'El Eterno', text)
    text = re.sub(r'^Señor\b', 'El Eterno', text, flags=re.MULTILINE)
    text = re.sub(r'\bSeñor\b', 'el Eterno', text)

    for orig, tok in senor_prot:
        text = text.replace(tok, orig)

    # ══════════════════════════════════════════════
    # 5. MINÚSCULAS TRAS PUNTO
    # ══════════════════════════════════════════════

    text = re.sub(r'\. ([a-záéíóúüñ])', lambda m: '. ' + m.group(1).upper(), text)

    return text


# ── Procesar todos los archivos ──────────────────
changed = 0
for fname in sorted(os.listdir(VOL3)):
    if not fname.endswith(".md"):
        continue
    fpath = os.path.join(VOL3, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        original = f.read()
    corrected = apply_corrections(original)
    if corrected != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(corrected)
        changed += 1
        print(f"  ✓ {fname}")

print(f"\nTotal archivos modificados: {changed} de 134")
