#!/usr/bin/env python3
import argparse
import asyncio
import json
from dataclasses import dataclass
from pathlib import Path

import aiomysql

from app.config import DB_CONFIG
from app.db.schema import apply_schema
from app.utils.text import normalize


ROOT = Path(__file__).resolve().parent
IMPORT_ROOT = ROOT / "import"


@dataclass(frozen=True)
class CatalogHymn:
    source_key: str
    language: str
    source_slug: str
    songbook: str
    number: int
    title: str
    content: str
    tune: str
    words: str


def read_json(path: Path):
    with path.open(encoding="utf-8-sig") as source:
        return json.load(source)


def load_catalog() -> tuple[list[CatalogHymn], list[str]]:
    hymns: list[CatalogHymn] = []
    warnings: list[str] = []
    for songs_path in sorted(IMPORT_ROOT.glob("*/*/songs.json")):
        folder = songs_path.parent
        language = folder.parent.name
        metadata = read_json(folder / "songbook.json")
        metadata = metadata[0] if isinstance(metadata, list) and metadata else metadata
        songbook = str((metadata or {}).get("title") or folder.name).strip()
        songs = read_json(songs_path)
        if isinstance(songs, dict):
            songs = songs.get("Songs") or songs.get("songs") or songs.get("data") or []
        if not isinstance(songs, list):
            warnings.append(f"{songs_path}: unsupported songs format")
            continue
        for index, song in enumerate(songs, start=1):
            title = str(song.get("title") or "").strip()
            content = str(song.get("song_text") or "").strip()
            if not title and not content:
                warnings.append(f"{language}/{folder.name} row {index}: empty record skipped")
                continue
            number = song.get("number") or index
            try:
                number = int(number)
            except (TypeError, ValueError):
                warnings.append(f"{language}/{folder.name} row {index}: invalid number {number!r}")
                number = index
            hymns.append(CatalogHymn(
                source_key=f"{language}/{folder.name}/{index}",
                language=language,
                source_slug=folder.name,
                songbook=songbook,
                number=number,
                title=title or f"Гимн {number}",
                content=content,
                tune=str(song.get("tune") or "").strip(),
                words=str(song.get("words") or "").strip(),
            ))
    return hymns, warnings


def print_audit(hymns: list[CatalogHymn], warnings: list[str]) -> None:
    counts: dict[tuple[str, str, str], int] = {}
    for hymn in hymns:
        key = (hymn.language, hymn.source_slug, hymn.songbook)
        counts[key] = counts.get(key, 0) + 1
    print(f"Catalog: {len(counts)} songbooks, {len(hymns)} usable hymns")
    for (language, slug, title), count in sorted(counts.items()):
        print(f"  {language}/{slug}: {count} — {title}")
    for warning in warnings:
        print(f"WARNING: {warning}")


async def get_or_create_songbook(cursor, hymn: CatalogHymn, order: int) -> int:
    await cursor.execute(
        "SELECT id FROM songbooks WHERE language_code=%s AND source_slug=%s",
        (hymn.language, hymn.source_slug),
    )
    row = await cursor.fetchone()
    if not row:
        await cursor.execute(
            "SELECT id FROM songbooks WHERE normalized_title=%s ORDER BY id LIMIT 1",
            (normalize(hymn.songbook),),
        )
        row = await cursor.fetchone()
    search_key = f"{hymn.language}:{hymn.source_slug}"
    if row:
        await cursor.execute(
            """UPDATE songbooks SET title=%s, normalized_title=%s, search_key=%s,
            language_code=%s, source_slug=%s, display_order=%s WHERE id=%s""",
            (hymn.songbook, normalize(hymn.songbook), search_key, hymn.language,
             hymn.source_slug, order, row["id"]),
        )
        return row["id"]
    await cursor.execute(
        """INSERT INTO songbooks
        (title, normalized_title, search_key, language_code, source_slug, display_order)
        VALUES (%s, %s, %s, %s, %s, %s)""",
        (hymn.songbook, normalize(hymn.songbook), search_key, hymn.language, hymn.source_slug, order),
    )
    return cursor.lastrowid


async def import_catalog(hymns: list[CatalogHymn]) -> None:
    pool = await aiomysql.create_pool(**DB_CONFIG, autocommit=False, minsize=1, maxsize=2)
    try:
        await apply_schema(pool)
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                book_ids: dict[tuple[str, str], int] = {}
                for hymn in hymns:
                    key = (hymn.language, hymn.source_slug)
                    if key not in book_ids:
                        book_ids[key] = await get_or_create_songbook(cursor, hymn, len(book_ids))
                inserted = updated = 0
                for hymn in hymns:
                    songbook_id = book_ids[(hymn.language, hymn.source_slug)]
                    await cursor.execute("SELECT id FROM hymns WHERE source_key=%s", (hymn.source_key,))
                    existing = await cursor.fetchone()
                    if not existing:
                        await cursor.execute(
                            """SELECT id FROM hymns
                            WHERE songbook_id=%s AND number=%s AND title_normalized=%s
                            ORDER BY id LIMIT 1""",
                            (songbook_id, hymn.number, normalize(hymn.title)),
                        )
                        existing = await cursor.fetchone()
                    values = (
                        hymn.title, hymn.content, songbook_id, hymn.number, hymn.tune, hymn.words,
                        hymn.source_key, hymn.source_key.replace("/", "_"),
                        normalize(hymn.title), normalize(hymn.content),
                    )
                    if existing:
                        await cursor.execute(
                            """UPDATE hymns SET title=%s, content=%s, songbook_id=%s, number=%s,
                            tune=%s, words=%s, source_key=%s, search_key=%s,
                            title_normalized=%s, content_normalized=%s WHERE id=%s""",
                            (*values, existing["id"]),
                        )
                        updated += 1
                    else:
                        await cursor.execute(
                            """INSERT INTO hymns
                            (title, content, songbook_id, number, tune, words, source_key,
                             search_key, title_normalized, content_normalized)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            values,
                        )
                        inserted += 1
                    if (inserted + updated) % 500 == 0:
                        print(f"Processed {inserted + updated}/{len(hymns)}")
                await conn.commit()
                print(f"Import complete: inserted={inserted}, updated={updated}")
    finally:
        pool.close()
        await pool.wait_closed()


async def main() -> None:
    parser = argparse.ArgumentParser(description="Audit and import every language/songbook into MySQL")
    parser.add_argument("--apply", action="store_true", help="write changes to MySQL (default: audit only)")
    args = parser.parse_args()
    hymns, warnings = load_catalog()
    print_audit(hymns, warnings)
    if args.apply:
        await import_catalog(hymns)
    else:
        print("Dry run only. Use --apply to write to MySQL.")


if __name__ == "__main__":
    asyncio.run(main())
