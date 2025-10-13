#!/usr/bin/env python3
"""
Päivittää manifest.jsonin tentit-hakemiston JSON-tiedostojen perusteella.

- Hakee kaikki *.json-tiedostot (mutta ohittaa manifest.jsonin).
- Säilyttää aiemmin manifestissa olleet lisäkentät (esim. kuvaus).
- Lisää/ajoittaa kategorian automaattisesti tiedostonimen perusteella.
- Luo luettavat otsikot (muuttaa _ ja - välilyönneiksi, isolla alkukirjaimella).
- Kirjoittaa manifest.jsonin kauniisti sisennettynä (UTF-8, indent=2).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Dict, Iterable, List

TITLE_KEYS: tuple[str, ...] = ("title", "name", "otsikko", "nimi", "subject")
MANIFEST_FILENAME = "manifest.json"

CATEGORY_ORDER = ["Fysiikka", "Ohjelmointi", "Tietotekniikka", "Muut"]
CATEGORY_PRIORITY = {name: index for index, name in enumerate(CATEGORY_ORDER)}

SMALL_WORDS = {"ja", "sekä", "tai", "ja", "vai"}


@dataclass
class Entry:
    id: str
    title: str
    file: str
    extras: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {"id": self.id, "title": self.title, "file": self.file}
        if self.extras:
            data.update(self.extras)
        return data


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-{2,}", "-", value).strip("-") or "tentti"


def prettify_title(filename: str) -> str:
    stem = Path(filename).stem
    words = re.split(r"[_\-\s]+", stem)
    if not words:
        return stem.capitalize()
    pretty = [words[0].capitalize()]
    for word in words[1:]:
        if word.lower() in SMALL_WORDS:
            pretty.append(word.lower())
        else:
            pretty.append(word.capitalize())
    return " ".join(pretty)


def load_manifest(path: Path) -> Dict[str, Entry]:
    if not path.exists() or path.stat().st_size == 0:
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"⚠️  Virhe: {path.name} ei ole kelvollista JSONia, luodaan uusi manifest.")
        return {}

    entries: Dict[str, Entry] = {}
    for raw in data:
        file = raw.get("file")
        if not isinstance(file, str):
            continue
        entry = Entry(
            id=raw.get("id") or slugify(Path(file).stem),
            title=raw.get("title") or raw.get("label") or prettify_title(file),
            file=file,
            extras={k: v for k, v in raw.items() if k not in {"id", "title", "label", "file"}},
        )
        entries[file] = entry
    return entries


def extract_title(data: Any, fallback: str) -> str:
    if isinstance(data, dict):
        for key in TITLE_KEYS:
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        for value in data.values():
            title = extract_title(value, fallback)
            if title != fallback:
                return title
    elif isinstance(data, list):
        for item in data:
            title = extract_title(item, fallback)
            if title != fallback:
                return title
    return fallback


def infer_category_from_filename(filename: str) -> str:
    name = filename.lower()
    if "ohjelmointi" in name:
        return "Ohjelmointi"
    if "fysiikka" in name:
        return "Fysiikka"
    if "tietotekniikka" in name or "it" in name or "tieto" in name:
        return "Tietotekniikka"
    return "Muut"


def gather_entries(manifest: Dict[str, Entry], tent_files: Iterable[Path]) -> List[Entry]:
    results: List[Entry] = []
    for file_path in tent_files:
        rel_name = file_path.name
        data = json.loads(file_path.read_text(encoding="utf-8"))
        previous = manifest.get(rel_name)

        title = extract_title(data, previous.title if previous else prettify_title(rel_name))
        category = (
            previous.extras.get("category")
            if previous and "category" in previous.extras
            else infer_category_from_filename(rel_name)
        )

        entry = previous or Entry(
            id=slugify(file_path.stem),
            title=title,
            file=rel_name,
            extras={},
        )

        extras = dict(entry.extras)
        extras["category"] = category

        if entry.title != title or entry.extras != extras:
            entry = replace(entry, title=title, extras=extras)

        results.append(entry)

    def sort_key(item: Entry) -> tuple[int, str]:
        category = item.extras.get("category", "Muut")
        priority = CATEGORY_PRIORITY.get(category, len(CATEGORY_PRIORITY))
        return priority, category.lower(), item.title.lower()

    results.sort(key=sort_key)
    return results


def main() -> None:
    root = Path(__file__).resolve().parent
    manifest_path = root / MANIFEST_FILENAME

    tent_files = [
        path
        for path in root.glob("*.json")
        if path.name.lower() != MANIFEST_FILENAME.lower()
    ]

    manifest_entries = load_manifest(manifest_path)
    updated_entries = gather_entries(manifest_entries, tent_files)

    manifest_path.write_text(
        json.dumps([entry.to_dict() for entry in updated_entries], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Päivitetty {manifest_path} ({len(updated_entries)} tenttiä).")


if __name__ == "__main__":
    main()
