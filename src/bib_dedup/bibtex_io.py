from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase


@dataclass(frozen=True)
class BibEntrySource:
    path: Path
    key: str


@dataclass(frozen=True)
class ExcludedBibEntry:
    path: Path
    reason: str
    entry: dict


def read_bib_file_with_exclusions(path: Path) -> tuple[list[dict], list[ExcludedBibEntry]]:
    parser = BibTexParser(common_strings=True)
    text = path.read_text(encoding="utf-8", errors="replace")
    db = bibtexparser.loads(text, parser=parser)

    entries: list[dict] = []
    excluded: list[ExcludedBibEntry] = []
    for entry in db.entries:
        # Ensure keys exist in the expected shape.
        if "ID" not in entry or "ENTRYTYPE" not in entry:
            excluded.append(
                ExcludedBibEntry(
                    path=path,
                    reason="missing_id_or_entrytype",
                    entry=dict(entry),
                )
            )
            continue
        entry = dict(entry)
        entry["__source_path"] = str(path)
        entries.append(entry)

    return entries, excluded


def read_bib_file(path: Path) -> list[dict]:
    entries, _excluded = read_bib_file_with_exclusions(path)
    return entries


def read_bib_files_with_exclusions(paths: Iterable[Path]) -> tuple[list[dict], list[ExcludedBibEntry]]:
    all_entries: list[dict] = []
    all_excluded: list[ExcludedBibEntry] = []
    for path in paths:
        entries, excluded = read_bib_file_with_exclusions(path)
        all_entries.extend(entries)
        all_excluded.extend(excluded)
    return all_entries, all_excluded


def read_bib_files(paths: Iterable[Path]) -> list[dict]:
    entries, _excluded = read_bib_files_with_exclusions(paths)
    return entries


def write_bib_file(path: Path, entries: list[dict]) -> None:
    # Remove internal metadata keys before writing.
    cleaned: list[dict] = []
    for entry in entries:
        out = {k: v for k, v in entry.items() if not k.startswith("__")}
        cleaned.append(out)

    db = BibDatabase()
    db.entries = cleaned

    writer = BibTexWriter()
    writer.indent = "  "
    writer.order_entries_by = None

    text = bibtexparser.dumps(db, writer=writer)
    path.write_text(text, encoding="utf-8")
