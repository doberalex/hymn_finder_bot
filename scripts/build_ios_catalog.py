#!/usr/bin/env python3
"""Build the compact, offline hymn catalogue bundled with the iOS app."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPORT_ROOT = ROOT / "import"
OUTPUT = ROOT / "ios/HymnFinder/HymnFinder/Resources/hymns.json"
LANGUAGE_NAMES = {"ru": "Русский", "uk": "Українська", "en": "English", "uz": "O‘zbekcha"}


def read_json(path: Path):
    with path.open(encoding="utf-8-sig") as source:
        return json.load(source)


def main() -> None:
    hymns: list[dict] = []
    for songs_path in sorted(IMPORT_ROOT.glob("*/*/songs.json")):
        folder = songs_path.parent
        language = folder.parent.name
        metadata = read_json(folder / "songbook.json")
        songbook = metadata[0].get("title", folder.name) if metadata else folder.name
        songs = read_json(songs_path)
        if isinstance(songs, dict):
            songs = songs.get("Songs") or songs.get("songs") or songs.get("data") or []

        for index, song in enumerate(songs, start=1):
            title = str(song.get("title") or "").strip()
            text = str(song.get("song_text") or "").strip()
            if not title and not text:
                continue
            number = song.get("number") or index
            try:
                number = int(number)
            except (TypeError, ValueError):
                number = index
            hymns.append(
                {
                    "id": f"{language}/{folder.name}/{index}",
                    "number": number,
                    "title": title or f"Гимн {number}",
                    "text": text,
                    "tune": str(song.get("tune") or "").strip(),
                    "words": str(song.get("words") or "").strip(),
                    "songbook": songbook,
                    "language": language,
                    "languageName": LANGUAGE_NAMES.get(language, language.upper()),
                }
            )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as destination:
        json.dump(hymns, destination, ensure_ascii=False, separators=(",", ":"))
    print(f"Wrote {len(hymns):,} hymns to {OUTPUT} ({OUTPUT.stat().st_size / 1_048_576:.1f} MB)")


if __name__ == "__main__":
    main()
