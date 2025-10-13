# TiTeTenttaaja

TiTeTenttaaja on monivalintatentti-harjoittelualusta, josta löytyy kolme käyttöliittymää: komentorivisovellus, selainversio ja Tauri-pohjainen desktop-sovellus. Kaikki versiot käyttävät samaa `tentit/`-hakemistoa ja `manifest.json` -tiedostoa.

## Projektin rakenne

- `titetenttaaja.py` – komentoriviversio.
- `WEB/` – selainkäyttöliittymä (HTML/CSS/JS). Lukee tentit juuren `tentit/`-hakemistosta.
- `tauri-app/` – Tauri-projekti desktop-sovellusta varten.
- `tentit/` – varsinaiset tenttikysymykset (`*.json`) ja `manifest.json`, jonka perusteella valikko rakentuu.
- `tentit/update_tentit.py` – apuskripti, joka synkronoi manifestin tenttitiedostoista.

## Käyttö

### Edellytykset

- Komentorivi/selainversio: Python 3.
- Desktop-versio: lisäksi Node.js (/npm) ja Rust toolchain (msvc Windowsilla).

### Komentoriviversio

1. Asenna riippuvuudet (tarvittaessa `pip install -r requirements.txt`).
2. Suorita projektin juuresta:
   ```bash
   python titetenttaaja.py
   ```
3. Valitse tentti ja seuraa ohjelman ohjeita.

### Selainversio

1. Käynnistä paikallinen palvelin projektin juuresta (esim. Pythonin sisäinen):
   ```bash
   python -m http.server
   ```
2. Avaa selain osoitteeseen `http://localhost:8000/WEB/`.
3. Valitse tentti, rajaa halutessasi kysymysten määrä ja aloita testi.

> Huom: selainversio lukee tentit polusta `../tentit/manifest.json`, joten se pitää ajaa palvelimen kautta juurihakemistosta.

### Desktop (Tauri)

1. Asenna Node.js ja Rust (Windowsilla myös MSVC Build Tools).
2. Projektin juuresta:
   ```bash
   cd tauri-app
   npm install
   ```
3. Kehitysmoodi:
   ```bash
   npm run tauri dev
   ```
4. Tuotantoversio:
   ```bash
   npm run tauri build
   ```
   Binääri löytyy `tauri-app/src-tauri/target/release/`-hakemistosta. MSI- ja NSIS-asentajat syntyvät vastaaviin `bundle/msi` ja `bundle/nsis` -hakemistoihin.

## Tenttien hallinta

Selain- ja desktop-versiot käyttävät samaa manifestia. Uuden tentin lisääminen:

1. Lisää uusi kysymystiedosto `tentit/`-hakemistoon (esim. `ohjelmistosuunnittelu.json`).
2. Synkronoi manifesti komennolla:
   ```bash
   python tentit/update_tentit.py
   ```
   Skripti
   - kerää kaikki `tentit/*.json`-tiedostot (paitsi `manifest.json`)
   - muodostaa tai päivittää `id`, `title`, `file` ja `category` -kentät
   - järjestää tentit kategorioittain (`Fysiikka`, `Ohjelmointi`, `Tietotekniikka`, `Muut`).
3. Käynnistä haluamasi käyttöliittymä – uusi tentti ilmestyy listalle automaattisesti.

Manifestin rivit näyttävät skriptin jälkeen tältä:

```json
{
  "id": "ohjelmistosuunnittelu",
  "title": "Ohjelmistosuunnittelu",
  "file": "ohjelmistosuunnittelu.json",
  "category": "Tietotekniikka"
}
```

Voit halutessasi muuttaa `category`-kentän arvoa käsin, jos automaattinen tunnistus ei vastaa toivottua ryhmää.

### Tentti-JSON:n rakenne

```json
{
  "TITLE": "Tietotekniikan perusteet",
  "questions": [
    {
      "question": "Mikä seuraavista on tietokoneen pysyvä, ei-katoava muisti?",
      "options": [
        "RAM-muisti",
        "ROM-muisti",
        "Näytönohjain",
        "Prosessori"
      ],
      "correct": "ROM-muisti"
    },
    {
      "question": "Kuinka monta bittiä muodostaa yhden tavun?",
      "options": ["4 bittiä", "8 bittiä", "16 bittiä", "32 bittiä"],
      "correct": "8 bittiä"
    }
  ]
}
```

- `TITLE` on vapaaehtoinen, mutta se käytetään manifestin oletusotsikkona.
- `question` on kysymysteksti, `options` sisältää vastausvaihtoehdot ja `correct` kertoo oikean vaihtoehdon.

## Vinkkejä kehitykseen

- Web- ja Tauri-versiot hyödyntävät samaa `WEB/app.js`-logiikkaa kattoakseen tenttien ryhmittelyn ja kysymysrajausten käsittelyn.
- Tyylit löytyvät `WEB/styles.css`-tiedostosta, ja niitä käyttää myös Tauri-versio.
- Jos lisäät uuden kategorian, muista päivittää sekä `tentit/update_tentit.py` että käyttöliittymien kategoriolistaukset.
