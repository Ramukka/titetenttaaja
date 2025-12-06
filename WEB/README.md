# TiTeTenttaaja

TiTeTenttaaja on monivalintatentti-harjoittelualusta, josta löytyy kolme käyttöliittymää: komentorivisovellus, selainversio ja Tauri-pohjainen desktop-sovellus. Kaikki versiot käyttävät samaa `TENTIT/`-hakemistoa ja `manifest.json` -tiedostoa.

## Sisällysluettelo

- [Tiivistelmä](#tiivistelmä)
- [Toiminnot](#toiminnot)
- [OHJEET FORKKAAJILLE](#ohjeet-forkkaajille)
- [Kuinka lisätä tenttejä](#kuinka-lisätä-tenttejä)
- [Oma testiympäristö (start_web.py)](#oma-testiympäristö-start_webpy)
- [Kuvien lisääminen](#kuvien-lisääminen)
- [Projektin rakenne](#projektin-rakenne)
- [Vaihtoehtoinen asennus (Tauri)](#vaihtoehtoinen-asennus-tauri)
- [Kehitysvinkkejä](#kehitysvinkkejä)

## Tiivistelmä

**🎓 Tervetuloa TiTeTenttaaja-tenttiapuriin!**

TiTeTenttaaja on joustava monivalintatentti-harjoittelualusta, jonka on suunnitellut **Tite24**. Se auttaa sinua oppimistehtävissä ja kokeisiin valmistautumisessa. Sovellus on saatavilla kolmessa versiossa: selainversiossa, komentorivisovelluksessa ja desktop-sovelluksessa.

**Mitä voit tehdä:**
- 📝 **Harjoittele monivalintakysymyksillä** – Tuhansia kysymyksiä eri aiheista
- ➕ **Lisää omia tenttejä** – Luo uusia tenttejä helposti ChatGPT:n avulla
- 📊 **Seuraa edistymistäsi** – Näe pistemäärä ja virheellisesti vastattavat kysymykset
- 🎨 **Valitse teema** – Tumma tai vaalea näkymä
- 📚 **Lue oppimateriaalia** – Joissakin tenteihin kuuluu myös lukumateriaalia

**Versiot:**

1. **Selainaversio** (suositeltu) – Nopein tapa päästä alkuun
   - Paikallisesti: `python start_web.py`
   - Online: https://titetenttaaja.onrender.com/
2. **Komentorivisovellus** – Klassinen terminaalikokemus
   - Käynnistä: `python titetenttaaja.py`
3. **Desktop-sovellus** (Tauri) – Erillinen Windows/Mac-sovellus
   - Asennusohje: katso alempaa

**Pääasiallinen idea:** Kaikki versiot käyttävät **samaa tenttimaterialia** (`TENTIT/`-kansiosta), joten voit lisätä uusia tenttejä kerran ja ne päivittyvät automaattisesti kaikkiin versioihin.

**Edellytykset:** Python 3.8+, `pip install -r requirements.txt`

---

## Toiminnot

✅ **Monivalintakysymykset** – Sekalaiset kysymykset 4 vastausvaihtoehdolla  
✅ **Lukumateriaali** – Kuvien ja tekstin yhdistelmä oppimista varten  
✅ **Kategoriointi** – Tentit jaetaan Fysiikka, Ohjelmointi, Tietotekniikka jne. -kategorioihin  
✅ **Pisteiden laskenta** – Näet oikeiden vastausten määrän ja väärät vastaukset lopussa  
✅ **Teemavalinta** – Tumma ja vaalea tila  
✅ **PDF → PNG muunnos** – Muunna PDF-materiaalit kuviksi automaattisesti  
✅ **Automaattinen synkronointi** – Uudet tentit päivittyvät kaikkiin versioihin yhdellä komennolla

---

## OHJEET FORKKAAJILLE

### ✅ Sallittuja toimenpiteitä (safe to push)

- **Tenttien lisääminen** – Uudet `.json`-tiedostot `TENTIT/`-kansioon
- **Kuvien lisääminen** – PNG-kuvat `TENTIT/images/`-kansioon
- **Lähdemateriaalien lisääminen** – PDF- ja Word-tiedostot `LAHDEMATERIAALIT/`-kansioon
- **PNG-muuntaminen** – Aja `pdf_to_images.py` PDF:ien muuntamiseen
- **Tiedostojen lisäys** – Dokumentaatio, lisenssit jne.

### ❌ EI sallittuja (älä push)

- **Koodin muuttaminen** – `*.py`, `*.js`, `*.rs`, `*.toml` jne.
- **Konfiguraatioiden muuttaminen** – `tauri.conf.json`, `Cargo.toml`, `package.json` jne.
- **Hakemistorakenteen muuttaminen** – Hakemistojen uudelleennimeäminen tai siirtäminen

### 📋 Ennen push:a

1. **Testaa paikallisesti:**
   ```bash
   python start_web.py
   ```
   Varmista että uudet tentit näkyvät ja toimivat oikein.

2. **Synkronoi kaikki versiot:**
   ```bash
   python TENTIT/update_tentit.py
   ```

3. **Tee commit vain tenteihin/kuviin:**
   ```bash
   git add TENTIT/
   git add LAHDEMATERIAALIT/
   git commit -m "Add new exams or images"
   git push origin main
   ```

4. **Älä committoi:**
   - `WEB/tentit/` – synkronoidaan automaattisesti
   - Muita `.py` tai `.js` tiedostoja
   - Konfiguraatiotiedostoja

---

## Kuinka lisätä tenttejä

### ChatGPT-prompt tenttikysymysten generointiin

Jos haluat luoda uusia tenttikysymyksiä ChatGPT:llä, käytä tätä promptia. Se varmistaa, että kysymykset ovat oikeanlaisen vaikeusasteisia ja hyvin strukturoituja.

**Kopioi tämä prompt ChatGPT:hen ja liitä oppimateriaali:**

```
Olet tenttimateriaalin asiantuntija. Sinulle annetaan oppimateriaali aiheesta [AIHE]. 

TEHTÄVÄ: Luo KAIKKI mahdolliset monivalintakysymykset annetusta materiaalista (vähintään 10, mieluummin 15-30).

VAATIMUKSET:
- 4 vastausvaihtoehtoa per kysymys (1 oikea, 3 väärä)
- Väärät vastaukset tulee olla uskottavia ja lähellä oikeaa vastausta
- Jos materiaali sisältää kuvia, luo kysymyksiä joissa mainitaan "Kuviossa X..."
- Sekoita oikean vastauksen sijainti (ei aina kohdassa 0)
- Merkitse vaikeusaste (helppo/keskitaso/vaikea) ja lähde jokaiselle kysymykselle

PALAUTUSMUOTO - JSON:
```json
{
  "TITLE": "[AIHE]",
  "questions": [
    {
      "question": "Kysymyksen teksti?",
      "options": ["Oikea", "Väärä 1", "Väärä 2", "Väärä 3"],
      "correct": "Oikea"
    }
  ]
}
```

MATERIAALI:
[LIITÄ TÄHÄN TEKSTISI TAI PDF:N SISÄLTÖ]
```

**Ohjeita promptin käyttöön:**

1. **Korvaa `[AIHE]`** – Kirjoita tenttiaiheen nimi (esim. "Python-ohjelmointi")
2. **Liitä materiaali** – Kopioi PDF:n tai oppkirjan teksti kohtaan `[LIITÄ TÄHÄN...]`
3. **Lähetä ChatGPT:lle** – Kopioi koko prompt ChatGPT:hen
4. **Kopioi JSON-vastaus** – ChatGPT palauttaa JSON-muotoisen kysymyslistan
5. **Liitä `TENTIT/`-kansioon** – Tallenna tiedostoksi esim. `TENTIT/python_tentti.json`
6. **Synkronoi:** `python TENTIT/update_tentit.py`

**Prompin vahvuudet:**
- ✅ Luo KAIKKI mahdolliset kysymykset (ei kiinteää määrää)
- ✅ Väärät vastaukset ovat uskottavia ja hankalia
- ✅ Tukee kuvien sisältäviä kysymyksiä
- ✅ Merkitsee vaikeusasteet ja lähteet
- ✅ JSON-muoto sopii suoraan sovellukseen

### Synkronointi

Kun olet lisännyt uuden tentin, aja synkronointikomento:

```bash
python TENTIT/update_tentit.py
```

Tämä komento:
- Päivittää `manifest.json`-tiedoston
- Kopioi kaikki JSON-tiedostot → `WEB/tentit/`
- Kopioi kuvat → `WEB/tentit/images/`

### Testaus

Käynnistä haluamasi versio ja näet uuden tentin listalla:

```bash
python start_web.py
```

---

## Oma testiympäristö (start_web.py)

**Nopein tapa testata sovellusta selaimessa:**

```bash
python start_web.py
```

Tämä skripti:
- Käynnistää HTTP-palvelimen portissa 3000
- Avaa selaimen osoitteeseen `http://localhost:3000/WEB/index.html`
- Tulostaa terminaaliin: `🚀 Open page: http://localhost:3000/WEB/index.html`

Palvelimen pysäyttäminen: `Ctrl+C`

**Vaihtoehto (manuaalinen):**
```bash
python -m http.server 3000
# Avaa sitten selaimessa: http://localhost:3000/WEB/index.html
```

**Komentoriviversio:**
```bash
python titetenttaaja.py
```

---

## Kuvien lisääminen

### PDF-kuvien muuntaminen PNG-muotoon

Jos materiaalisi on PDF-muodossa, voit muuntaa sen PNG-kuviksi:

#### 1. Asenna Poppler

**Windows (WinGet) - SUOSITELTU:**
```bash
winget install oschwartz10612.Poppler
```

Asennuksen jälkeen Poppler löytyy automaattisesti.

**Linux:**
```bash
sudo apt-get install poppler-utils  # Ubuntu/Debian
sudo dnf install poppler-utils      # Fedora
```

**macOS:**
```bash
brew install poppler
```

#### 2. Muunna PDF kuviksi

Kopioi PDF-tiedostosi `LAHDEMATERIAALIT/`-hakemistoon ja aja:

```bash
cd LAHDEMATERIAALIT
python pdf_to_images.py
```

Skripti kysyy:
1. **PDF-tiedoston nimi** (esim. `Chap02.pdf`)
2. **Aloitusnumero** (oletus: 1)
3. **Kansion nimi kuvien tallennukseen** (oletus: PDF:n nimi)

**Esimerkki:**
```
PDF-tiedoston nimi: Elektroniikka.pdf
Aloitusnumero: 1
Kansion nimi: elektroniikka

✨ Valmis! Luotiin kuvat 1-23 -> TENTIT/images/elektroniikka
```

#### 3. Viittaa kuviin kysymyksissä

```json
{
  "question": "Mikä on Ohmin laki?",
  "image": "./images/elektroniikka/12.png",
  "options": [...],
  "correct": "..."
}
```

---

## Projektin rakenne

- `titetenttaaja.py` – komentoriviversio.
- `start_web.py` – HTTP-palvelimen käynnistysskripti.
- `WEB/` – selainkäyttöliittymä (HTML/CSS/JS).
- `TENTIT/` – **pääkansio** kaikille tenttikysymyksille ja manifestille.
  - `images/` – kuvatiedostot (PNG-muodossa).
  - `update_tentit.py` – synkronointiskripti.
- `LAHDEMATERIAALIT/` – lähtömaterialit (PDF, Word, teksti).
  - `pdf_to_images.py` – PDF → PNG muunnin.
- `tauri-app/` – Desktop-sovellus (valinnainen).

### Tärkeimmät skriptit

| Skripti | Käyttö | Mitä tekee |
|---------|--------|------------|
| `start_web.py` | `python start_web.py` | Käynnistää palvelimen ja avaa selaimen |
| `titetenttaaja.py` | `python titetenttaaja.py` | Käynnistää komentorivisovelluksen |
| `TENTIT/update_tentit.py` | `python TENTIT/update_tentit.py` | Synkronoi tentit WEB-kansioon |
| `LAHDEMATERIAALIT/pdf_to_images.py` | `cd LAHDEMATERIAALIT; python pdf_to_images.py` | Muuntaa PDF-tiedostot PNG-kuviksi |

---

## Vaihtoehtoinen asennus (Tauri)

Desktop-sovellus vaatii Node.js ja Rust:n.

### 1. Asenna riippuvuudet

```bash
cd tauri-app
npm install
```

### 2. Synkronoi tenttitiedostot

```bash
xcopy /E /I /Y ..\TENTIT\*.json src\tentit\
xcopy /E /I /Y ..\TENTIT\images src\tentit\images
```

### 3. Kehitysmoodi

```bash
npm run tauri dev
```

### 4. Buildaa tuotanto

```bash
npm run tauri build
```

Binääri ja asentajat luodaan automaattisesti `src-tauri/target/release/bundle/`-hakemistoon:
- `msi/` – Windows MSI-asentusohjelma (suositeltu)
- `nsis/` – NSIS-asentusohjelma
- `tauri-app.exe` – Standalone-versio (ei asennusta)

---

## Kehitysvinkkejä

### Tentti-JSON:n rakenne

**Peruskysymykset:**
```json
{
  "TITLE": "Tietotekniikan perusteet",
  "questions": [
    {
      "question": "Mikä seuraavista on tietokoneen pysyvä muisti?",
      "options": ["RAM", "ROM", "Näytönohjain", "Prosessori"],
      "correct": "ROM"
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
      "text": "Sähköpiirien perusteita...",
      "image": "./images/elektroniikka/1.png"
    }
  ]
}
```

### Yleisiä ongelmia

**Kuvat eivät näy:**
- Tarkista että kuvatiedostot ovat `TENTIT/images/`-hakemistossa
- Tarkista polut JSON-tiedostoissa (`./images/...`)
- Windowsilla: Tarkista kirjainkoko tiedostonimissä

**Uusi tentti ei näy:**
- Aja `python TENTIT/update_tentit.py`

**Desktop-sovellus ei käynnisty:**
- Asenna WebView2 Runtime Windowsille
- Tarkista build: `npm run tauri build`

---

MIT License - vapaasti käytettävissä ja muokattavissa.
