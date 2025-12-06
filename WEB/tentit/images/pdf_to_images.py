#!/usr/bin/env python3
"""
Muuntaa PDF:n yksittäisiksi PNG-kuviksi.
Käyttö: python pdf_to_images.py <pdf-tiedosto> [aloitusnumero]

Esim: python pdf_to_images.py slides.pdf 8
      -> Luo kuvat 8.png, 9.png, 10.png, ...
"""

import sys
from pathlib import Path
from pdf2image import convert_from_path
import os
import glob

# Poppler-polku (winget-asennus)
# Käytetään glob-patternia löytämään versio automaattisesti
POPPLER_PATTERN = os.path.expandvars(r"$LOCALAPPDATA\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-*\Library\bin")

def find_poppler_path():
    """Etsii Poppler-asennuksen polun automaattisesti."""
    matches = glob.glob(POPPLER_PATTERN)
    if matches:
        # Palautetaan uusin versio (aakkos-/numerojärjestyksessä viimeinen)
        return sorted(matches)[-1]
    return None

POPPLER_PATH = find_poppler_path()

def pdf_to_images(pdf_path: str, start_number: int = 1, output_root: Path | None = None, subfolder: str | None = None):
    """
    Muuntaa PDF:n PNG-kuviksi.
    
    Args:
        pdf_path: Polku PDF-tiedostoon
        start_number: Ensimmäisen kuvan numero (oletus: 1)
    """
    pdf_file = Path(pdf_path)
    
    if not pdf_file.exists():
        print(f"❌ Tiedostoa ei löydy: {pdf_path}")
        return
    
    if pdf_file.suffix.lower() != '.pdf':
        print(f"❌ Tiedosto ei ole PDF: {pdf_path}")
        return
    
    print(f"📄 Käsitellään: {pdf_file.name}")
    
    # Muunnetaan PDF kuviksi (käytetään Poppler-polkua)
    try:
        images = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
        print(f"✅ Löydettiin {len(images)} sivua")
    except Exception as e:
        print(f"❌ Virhe PDF:n lukemisessa: {e}")
        print("\n💡 Varmista että Poppler on asennettu:")
        print("   Windows: winget install oschwartz10612.Poppler")
        if POPPLER_PATH:
            print(f"   Löydetty polku: {POPPLER_PATH}")
        else:
            print(f"   ⚠️ Poppler-asennusta ei löytynyt polusta: {POPPLER_PATTERN}")
        print("\n   Linux: sudo apt-get install poppler-utils")
        print("   macOS: brew install poppler")
        return
    
    # Tallennetaan kuvat
    root = output_root or Path(__file__).parent
    output_dir = root / subfolder if subfolder else root
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for i, image in enumerate(images):
        output_number = start_number + i
        output_path = output_dir / f"{output_number}.png"
        image.save(output_path, 'PNG')
        print(f"💾 Tallennettu: {output_path.name}")
    
    print(f"\n✨ Valmis! Luotiin kuvat {start_number}-{start_number + len(images) - 1} -> {output_dir}")

if __name__ == "__main__":
    # Interaktiivinen käyttöliittymä terminaaliin
    print("=== PDF -> PNG Muunnin ===\n")
    
    # Tarkista Poppler
    if not POPPLER_PATH:
        print("⚠️ Poppler-asennusta ei löytynyt automaattisesti!")
        print("Asenna Poppler komennolla: winget install oschwartz10612.Poppler\n")
    
    # Näytä nykyinen sijainti
    current_dir = Path(__file__).parent
    print(f"📂 Nykyinen hakemisto: {current_dir}")
    print(f"💾 Kuvat tallennetaan: {current_dir}/<kansion_nimi>/\n")
    
    # PDF-tiedoston nimi
    pdf_path = input("PDF-tiedoston nimi (esim. Chap02.pdf): ").strip()
    if not pdf_path:
        print("❌ PDF-tiedoston nimi vaaditaan!")
        sys.exit(1)
    
    # Aloitusnumero
    start_num_str = input("Anna kuville aloitusnumero (oletus: 1): ").strip() or "1"
    try:
        start_num = int(start_num_str)
    except ValueError:
        print("⚠️ Aloitusnumero ei ollut kokonaisluku, käytetään 1")
        start_num = 1
    
    # Alikansion nimi - käytetään PDF:n nimeä oletuksena
    pdf_stem = Path(pdf_path).stem  # Tiedostonimi ilman .pdf-päätettä
    default_folder = pdf_stem.lower().replace(" ", "_")
    subfolder_str = input(f"Kansion nimi kuvien tallennukseen (oletus: {default_folder}): ").strip() or default_folder
    
    # Tallennetaan aina nykyiseen images-hakemistoon
    output_root = Path(__file__).parent
    
    print(f"\n📁 Tallennetaan: {output_root / subfolder_str}/")
    print(f"🔢 Numeroidaan: {start_num}, {start_num+1}, {start_num+2}...\n")
    
    pdf_to_images(pdf_path, start_num, output_root=output_root, subfolder=subfolder_str)
