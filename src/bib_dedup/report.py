from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Optional

from .dedup import DedupResult
from .bibtex_io import ExcludedBibEntry


def write_report(path: Path, result: DedupResult, *, excluded: Optional[Iterable[ExcludedBibEntry]] = None) -> None:
    excluded_entries: list[dict[str, Any]] = []

    # 1) Entries explicitly skipped during parsing (invalid/unusable records)
    for ex in list(excluded or []):
        excluded_entries.append(
            {
                "reason": ex.reason,
                "source_path": str(ex.path),
                "id": ex.entry.get("ID"),
                "entrytype": ex.entry.get("ENTRYTYPE"),
                "title": ex.entry.get("title") or ex.entry.get("TITLE"),
            }
        )

    # 2) Duplicate entries that were not kept as the "winner" citekey
    for g in result.duplicate_groups:
        for e in g.entries:
            eid = str(e.get("ID") or "")
            if eid == g.kept_entry_id:
                continue
            excluded_entries.append(
                {
                    "reason": "duplicate",
                    "canonical_id": g.canonical_id,
                    "kept": {
                        "id": g.kept_entry_id,
                        "source_path": g.kept_source_path,
                    },
                    "excluded": {
                        "id": e.get("ID"),
                        "entrytype": e.get("ENTRYTYPE"),
                        "source_path": e.get("__source_path"),
                        "doi": e.get("doi") or e.get("DOI"),
                        "title": e.get("title") or e.get("TITLE"),
                        "year": e.get("year") or e.get("date"),
                    },
                }
            )

    data = {
        "unique_count": len(result.unique_entries),
        "duplicate_group_count": len(result.duplicate_groups),
        "excluded_count": len(excluded_entries),
        "excluded_entries": excluded_entries,
        "duplicate_groups": [
            {
                "canonical_id": g.canonical_id,
                "kept_entry_id": g.kept_entry_id,
                "kept_source_path": g.kept_source_path,
                "size": len(g.entries),
                "entries": [
                    {
                        "id": e.get("ID"),
                        "entrytype": e.get("ENTRYTYPE"),
                        "source_path": e.get("__source_path"),
                        "doi": e.get("doi") or e.get("DOI"),
                        "title": e.get("title") or e.get("TITLE"),
                        "year": e.get("year") or e.get("date"),
                    }
                    for e in g.entries
                ],
            }
            for g in result.duplicate_groups
        ],
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
