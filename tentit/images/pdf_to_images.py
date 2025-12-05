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

# Poppler-polku (winget-asennus)
POPPLER_PATH = os.path.expandvars(r"$LOCALAPPDATA\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-25.07.0\Library\bin")

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
        print("   Windows: Lataa https://github.com/oschwartz10612/poppler-windows/releases/")
        print("            ja lisää bin-kansio PATH-muuttujaan")
        print("   pip install pdf2image")
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
    pdf_path = input("Muunna PDF -> polku (esim. Chap02.pdf): ").strip() or "Chap02.pdf"
    start_num_str = input("Aloitusnumero (oletus 1): ").strip() or "1"
    output_root_str = input("Minne tallennetaan? (oletus nykyinen kansio): ").strip()
    subfolder_str = input("Kansion nimi (esim. 'export'): ").strip()

    try:
        start_num = int(start_num_str)
    except ValueError:
        print("⚠️ Aloitusnumero ei ollut kokonaisluku, käytetään 1")
        start_num = 1

    output_root = Path(output_root_str) if output_root_str else None

    pdf_to_images(pdf_path, start_num, output_root=output_root, subfolder=subfolder_str or None)
