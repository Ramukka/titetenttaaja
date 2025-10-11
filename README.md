# TiTeTenttaaja

Tenttijärjestelmä, jolla voit harjoitella monivalintakysymyksiä komentoriviltä, selaimessa ja desktop-sovelluksena (Tauri).

## Käyttö

### Kehittäjälle

#### CLI
1. Suorita projektin juuressa `python titetenttaaja.py` (Windows) tai `python3 titetenttaaja.py` (Linux/macOS).
2. Valitse tentti ja vastaa kysymyksiin.

#### Selainversio
1. Käynnistä juurihakemistosta paikallinen palvelin: `python -m http.server`.
2. Avaa selain osoitteeseen `http://localhost:8000/WEB/`.
3. Valitse tentti, rajaa tarvittaessa kysymysten määrä ja aloita testi.

#### Desktop (Tauri)
1. Asenna Node.js ja Rust toolchain (Windowsissa myös MSVC Build Tools).
2. Projektin juuresta: `cd tauri-app && npm install`.
3. Kehitysmoodi: `npm run tauri dev` avaa desktop-version.
4. Tuotantoversio: `npm run tauri build`. Valmis ajettava versio syntyy polkuun  
   `tauri-app/src-tauri/target/release/tauri-app.exe`.  
   MSI- ja NSIS-asentajat löytyvät `tauri-app/src-tauri/target/release/bundle/msi/…` ja `…/bundle/nsis/…`.  

### Loppukäyttäjälle

#### Desktop
1. Hanki kehittäjän tuottama `TiteTenttaaja.exe` tai `TiteTenttaaja_*_setup.exe`.
2. Suorita `TiteTenttaaja.exe` (tai asenna MSI/NSIS-paketilla) ja aloita tentti.  
   Pythonia, Nodea tai Rustia ei tarvita.

#### CLI (vaihtoehtoisesti)
1. Asenna Python 3 ja siirry projektin juureen.
2. Suorita `python titetenttaaja.py` ja seuraa ohjeita komentorivillä.

#### Selain (vaihtoehtoisesti)
1. Käynnistä juuresta `python -m http.server` (vaatii Pythonin).
2. Avaa `http://localhost:8000/WEB/` ja valitse tentti.
5. Tentit synkataan automaattisesti `tentit/`-kansiosta (manifest.json + JSON-tiedostot).

## Tenttien lisääminen

1. Lisää uusi JSON-tiedosto `tentit/`-hakemistoon.
2. Päivitä `tentit/manifest.json` lisäämällä rivi:
   ```json
   { "id": "uusi-id", "label": "Uusi tentti", "file": "uusi.json" }
   ```
   `id` on valikossa käytettävä tunniste, `label` näyttää tentin nimen ja `file` osoittaa JSON-tiedostoon.
3. Käynnistä selain- tai desktop-versio – uusi tentti ilmestyy automaattisesti valikkoon.

### JSON-tiedoston rakenne
```json
{
  "TITLE": "Tentin aihe",
  "questions": [
    {
      "question": "Kysymys",
      "options": [
        "Optio 1",
        "Optio 2",
        "Optio 3",
        "Optio 4"
      ],
      "correct": "Optio 1"
    }
  ]
}
```
