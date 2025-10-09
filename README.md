# TiTeTenttaaja

Komentorivipohjainen Python-tenttijärjestelmä, joka lukee kysymykset JSON-tiedostosta ja antaa monivalintakysymyksiä.

## Käyttö
1. Suorita 'python3 titetenttaaja.py'(Windows) tai 'python titetenttaaja.py'(Gnu/Linux)
2. valitse tentti ja vastaa kysymyksiin.

## Kontributoi

Tentit ovat JSON-tiedostoina projektin juuressa kansiossa nimeltä 'tentit'. voit luoda omia tenttitiedostoja ja lisätä ne repositorioon muiden saatavaksi.

JSON-tiedoston rakenne:
```json
[
	{"question": "Kysymys",
	 "options": ["Valinta1", "Valinta2", "Valinta3", "Valinta4"]}
]