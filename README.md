# TiTeTenttaaja

TiTeTenttaaja on monivalintatentti-harjoittelualusta, josta löytyy kolme käyttöliittymää: komentorivisovellus, selainversio ja Tauri-pohjainen desktop-sovellus. Kaikki versiot käyttävät samaa `tentit/`-hakemistoa ja `manifest.json` -tiedostoa.

## Sisällysluettelo

- [Projektin rakenne](#projektin-rakenne)
- [Käyttöönotto](#käyttöönotto)
- [Tenttikysymysten luominen](#tenttikysymysten-luominen)
- [Kuvien lisääminen](#kuvien-lisääminen)
- [Tenttien hallinta](#tenttien-hallinta)
- [Desktop-sovelluksen asennus](#desktop-sovelluksen-asennus)
- [Kehitysvinkkejä](#kehitysvinkkejä)

## Projektin rakenne

- `titetenttaaja.py` – komentoriviversio.
- `WEB/` – selainkäyttöliittymä (HTML/CSS/JS). Synkronoidaan automaattisesti `tentit/`-kansiosta.
- `tauri-app/` – Tauri-projekti desktop-sovellusta varten.
- `tentit/` – varsinaiset tenttikysymykset (`*.json`), lukumateriaali ja `manifest.json`.
  - `images/` – kuvatiedostot kysymyksille ja materiaalille (PNG-muodossa).
  - `update_tentit.py` – synkronointiskripti, joka päivittää manifestin ja kopioi kaiken `WEB/tentit/`-kansioon.
  - `images/pdf_to_images.py` – apuskripti PDF-tiedostojen muuntamiseen PNG-kuviksi.
- `lahdemateriaalit/` – lähtömateriaalit (PDF-, Word- ja tekstitiedostot).

## Käyttöönotto

### Edellytykset

- Python 3.8 tai uudempi
- Riippuvuudet: `pip install -r requirements.txt`
  - `rich` – komentorivikäyttöliittymä
  - `pdf2image` – PDF-kuvien käsittely
  - `Pillow` – kuvankäsittely
- Desktop-versio: lisäksi Node.js (npm) ja Rust toolchain (msvc Windowsilla).
- PDF-käsittely: Poppler-kirjasto (ks. [Kuvien lisääminen](#kuvien-lisääminen)).

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

## Tenttikysymysten luominen

### 1. Kysymysten generointi tekoälyllä

Voit käyttää tekoälyä (esim. ChatGPT, Claude, Gemini) kysymysten luomiseen:

1. **Anna materiaali tekoälylle** (esim. luentokalvot, oppikirja, muistiinpanot)
2. **Pyydä JSON-muotoisia kysymyksiä**:
   ```
   Luo 10 monivalintakysymystä tästä materiaalista JSON-muodossa. 
   Jokainen kysymys tarvitsee:
   - question: kysymysteksti
   - options: 4 vaihtoehtoa (lista)
   - correct: oikea vastaus
   - image: (valinnainen) kuvatiedoston polku
   ```

3. **Esimerkki tekoälyn vastauksesta**:
   ```json
   {
     "question": "Mikä on Ohmin laki?",
     "options": [
       "V = I × R",
       "P = V + I",
       "R = V - I",
       "I = R + V"
     ],
     "correct": "V = I × R",
     "image": "./images/chap02/OHM.png"
   }
   ```

### 2. JSON-tiedoston muodostaminen

Kopioi tekoälyn tuottamat kysymykset ja lisää ne tenttitiedostoon:

```json
{
  "TITLE": "Elektroniikan perusteet",
  "questions": [
    {
      "question": "Mitä sähkövirta tarkoittaa?",
      "options": [
        "Sähkövarauksen virtausta",
        "Sähköenergian varastointia",
        "Magneettikentän muutosta",
        "Lämpöenergian siirtymistä"
      ],
      "correct": "Sähkövarauksen virtausta"
    },
    ...
  ]
}
```

**Valinnainen: Lukumateriaali**

Voit luoda myös lukumateriaalia kysymysten tueksi:

```json
{
  "TITLE": "Elektroniikan perusteet - Lukumateriaali",
  "isReadingMaterial": true,
  "content": [
    {
      "title": "1. Johdanto",
      "text": "Luento käsittelee sähköpiirien perusteita...",
      "image": "./images/chap02/1.png"
    },
    ...
  ],
  "ORDER": 1
}
```

### 3. Tallenna ja synkronoi

1. **Tallenna tiedosto** `tentit/`-hakemistoon (esim. `tentit/elektroniikan_perusteet.json`)
2. **Päivitä manifest.json ja synkronoi WEB-kansio**:
   ```bash
   python tentit/update_tentit.py
   ```
   
   Tämä skripti:
   - Skannaa kaikki `tentit/*.json`-tiedostot ja lisää ne `manifest.json`-tiedostoon
   - Kopioi automaattisesti kaikki JSON-tiedostot ja kuvat `WEB/tentit/`-kansioon
   
   💡 **Ei tarvitse kopioida tiedostoja manuaalisesti!** Skripti hoitaa kaiken synkronoinnin.

### 4. Testaa ja julkaise

1. **Testaa paikallisesti** selaimessa tai desktop-sovelluksessa
2. **Commitoi ja pushaa GitHubiin**:
   ```bash
   git add tentit/elektroniikan_perusteet.json tentit/manifest.json
   git commit -m "Add Elektroniikan perusteet tentti"
   git push origin main
   ```

## Kuvien lisääminen

### PDF-kuvien muuntaminen PNG-muotoon

Jos materiaalisi on PDF-muodossa, voit muuntaa sen PNG-kuviksi:

#### 1. Asenna Poppler

**Windows (WinGet) - SUOSITELTU**:
```bash
winget install oschwartz10612.Poppler
```

Asennuksen jälkeen Poppler löytyy automaattisesti polusta `%LOCALAPPDATA%\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-XX.XX.X\Library\bin`

⚠️ **TÄRKEÄÄ**: Jos `pdf_to_images.py` valittaa Poppler-polusta, avaa skripti ja päivitä `POPPLER_PATH`-muuttuja vastaamaan asennettua versiota.

**Linux**:
```bash
sudo apt-get install poppler-utils  # Ubuntu/Debian
sudo dnf install poppler-utils      # Fedora
```

**macOS**:
```bash
brew install poppler
```

#### 2. Asenna Python-riippuvuudet

```bash
pip install pdf2image Pillow
```

#### 3. Muunna PDF kuviksi

**Valmistele PDF-tiedosto:**
1. Kopioi PDF-tiedostosi `tentit/images/`-hakemistoon väliaikaisesti
   - Esim: `tentit/images/Elektroniikka.pdf`
   - PDF:t voi siirtää `lahdemateriaalit/`-kansioon muunnoksen jälkeen

**Aja muunnosskripti:**

Skripti on interaktiivinen - se kysyy tarvittavat tiedot:

```bash
cd tentit/images
python pdf_to_images.py
```

**Kysyttävät tiedot:**

1. **PDF-tiedoston nimi** (esim. `Chap02.pdf`)
   - Tiedoston pitää olla samassa hakemistossa skriptin kanssa
   
2. **Aloitusnumero** (oletus: 1)
   - Ensimmäisen kuvan numero
   - Esim. jos haluat aloittaa numerosta 8, anna `8`
   
3. **Kansion nimi** (oletus: PDF:n nimi)
   - Kuvat tallennetaan `tentit/images/<kansion_nimi>/`
   - Oletus käyttää PDF:n nimeä (esim. `Chap02.pdf` → `chap02/`)
   - Voit antaa oman nimen, esim. `elektroniikka`

**Esimerkki käyttö:**

```
=== PDF -> PNG Muunnin ===

PDF-tiedoston nimi (esim. Chap02.pdf): Elektroniikka.pdf
Anna kuville aloitusnumero (oletus: 1): 1
Kansion nimi kuvien tallennukseen (oletus: elektroniikka): 

📁 Tallennetaan: tentit/images/elektroniikka/
🔢 Numeroidaan: 1, 2, 3...

📄 Käsitellään: Elektroniikka.pdf
✅ Löydettiin 23 sivua
💾 Tallennettu: 1.png
💾 Tallennettu: 2.png
...
✨ Valmis! Luotiin kuvat 1-23 -> tentit/images/elektroniikka
```

Skripti luo automaattisesti kansion ja tallentaa PNG-kuvat sinne muodossa `1.png`, `2.png`, `3.png` jne.

#### 4. Viittaa kuviin kysymyksissä

```json
{
  "question": "Mikä on Ohmin laki?",
  "image": "./images/chap02/12.png",
  "options": [...],
  "correct": "..."
}
```

Kuvien polut ovat suhteellisia `tentit/`-hakemistoon nähden. Web-sovellus muuntaa ne automaattisesti oikeiksi URL-osoitteiksi.

## Tenttien hallinta

Selain- ja desktop-versiot käyttävät samaa manifestia. Uuden tentin lisääminen:

1. Lisää uusi kysymystiedosto `tentit/`-hakemistoon (esim. `ohjelmistosuunnittelu.json`).
2. Synkronoi kaikki komennolla:
   ```bash
   python tentit/update_tentit.py
   ```
   
   **Skripti tekee automaattisesti:**
   - Päivittää `manifest.json`-tiedoston (lisää kaikki `tentit/*.json`-tiedostot)
   - Kopioi kaikki JSON-tiedostot → `WEB/tentit/`
   - Kopioi koko `images/`-kansion → `WEB/tentit/images/`
   - Järjestää tentit kategorioittain (`Fysiikka`, `Ohjelmointi`, `Tietotekniikka`, `Ohjelmistosuunnittelu`, `Muut`)
   
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

## Desktop-sovelluksen asennus

### Windowsille

Desktop-sovelluksesta luodaan kaksi asennusvaihtoehtoa:

#### 1. MSI-asennusohjelma (suositeltu)
- Löytyy: `tauri-app/src-tauri/target/release/bundle/msi/TiTeTenttaaja_X.X.X_x64_en-US.msi`
- Kaksoisklikkaa MSI-tiedostoa ja seuraa asennusohjelmaa
- Sovellus asentuu `Program Files` -hakemistoon
- Luo automaattisesti pikakuvakkeet

#### 2. NSIS-asennusohjelma
- Löytyy: `tauri-app/src-tauri/target/release/bundle/nsis/TiTeTenttaaja_X.X.X_x64-setup.exe`
- Tarjoaa enemmän kustomointimahdollisuuksia asennuksen aikana

#### 3. Standalone EXE (ei asennusta)
- Löytyy: `tauri-app/src-tauri/target/release/tauri-app.exe`
- Käynnistyy suoraan ilman asennusta
- Vaatii että kaikki riippuvuudet (WebView2) on asennettu järjestelmään

### Buildaaminen itse

```bash
cd tauri-app
npm install
npm run tauri build
```

Build-prosessi luo kaikki kolme versiota automaattisesti.

### Järjestelmävaatimukset

- **Windows 10/11** (64-bit)
- **WebView2 Runtime** (yleensä valmiiksi Windows 11:ssä)
  - Jos puuttuu: https://developer.microsoft.com/en-us/microsoft-edge/webview2/

## Kehitysvinkkejä

### Tentti-JSON:n rakenne

**Peruskysymykset:**
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
      "correct": "8 bittiä",
      "image": "./images/bits_and_bytes.png"
    }
  ]
}
```

**Lukumateriaali:**
```json
{
  "TITLE": "Elektroniikan perusteet - Lukumateriaali",
  "isReadingMaterial": true,
  "content": [
    {
      "title": "1. Johdanto",
      "text": "Luento käsittelee sähköpiirien perusteita...",
      "image": "./images/chap02/1.png"
    }
  ],
  "ORDER": 1
}
```

- `TITLE` on vapaaehtoinen, mutta se käytetään manifestin oletusotsikkona.
- `question` on kysymysteksti, `options` sisältää vastausvaihtoehdot ja `correct` kertoo oikean vaihtoehdon.
- `image` on valinnainen kenttä kuvalle (suhteellinen polku `tentit/`-hakemistosta).
- `isReadingMaterial: true` merkitsee tiedoston lukumateriaaliksi kysymysten sijaan.

### Koodin rakenne

- Web- ja Tauri-versiot hyödyntävät samaa `WEB/app.js`-logiikkaa kattoakseen tenttien ryhmittelyn ja kysymysrajausten käsittelyn.
- Tyylit löytyvät `WEB/styles.css`-tiedostosta, ja niitä käyttää myös Tauri-versio.
- Jos lisäät uuden kategorian, muista päivittää sekä `tentit/update_tentit.py` että käyttöliittymien kategoriolistaukset.

### Yleisiä ongelmia

**Kuvat eivät näy:**
- Tarkista että kuvatiedostot ovat `tentit/images/`-hakemistossa
- Tarkista että polut ovat oikein JSON-tiedostoissa (`./images/...`)
- Windowsilla: Tarkista että tiedostonimien kirjainkoko täsmää (esim. `BASIC.png` vs `basic.png`)

**Uusi tentti ei näy listalla:**
- Aja `python tentit/update_tentit.py` manifestin päivittämiseksi
- Kopioi tiedosto myös `WEB/tentit/`-hakemistoon web-versiota varten

**Desktop-sovellus ei käynnisty:**
- Asenna WebView2 Runtime Windowsille
- Tarkista että kaikki riippuvuudet on buildattu oikein (`npm run tauri build`)

---

## Lisenssi

MIT License - vapaasti käytettävissä ja muokattavissa.
