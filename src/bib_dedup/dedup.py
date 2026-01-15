from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable
from typing import Optional

from .normalize import (
    first_author_lastname,
    normalize_doi,
    normalize_title,
    parse_year,
)


@dataclass(frozen=True)
class DedupConfig:
    prefer_citekey: str = "best"  # 'best' or 'first'


@dataclass(frozen=True)
class DuplicateGroup:
    canonical_id: str
    kept_entry_id: str
    kept_source_path: Optional[str]
    entries: list[dict]


@dataclass(frozen=True)
class DedupResult:
    unique_entries: list[dict]
    duplicate_groups: list[DuplicateGroup]


def _entry_quality_score(entry: dict) -> int:
    # Simple heuristic: number of non-empty fields (excluding internal keys).
    score = 0
    for k, v in entry.items():
        if k in {"ID", "ENTRYTYPE"} or k.startswith("__"):
            continue
        if isinstance(v, str) and v.strip():
            score += 1
    # Prefer non-misc entry types.
    if (entry.get("ENTRYTYPE") or "").lower() != "misc":
        score += 1
    return score


def _pick_best_entry(entries: list[dict]) -> dict:
    return max(entries, key=_entry_quality_score)


def _pick_field_value(values: list[str]) -> str:
    candidates = [v.strip() for v in values if isinstance(v, str) and v.strip()]
    if not candidates:
        return ""
    # Prefer longer value as a proxy for specificity.
    return max(candidates, key=len)


def merge_entries(entries: list[dict], *, prefer_citekey: str) -> dict:
    if not entries:
        raise ValueError("merge_entries called with no entries")

    if prefer_citekey == "first":
        base = entries[0]
    else:
        base = _pick_best_entry(entries)

    merged: dict = {"ENTRYTYPE": base.get("ENTRYTYPE", "misc"), "ID": base.get("ID", "")}

    # Merge remaining fields.
    all_keys: set[str] = set()
    for e in entries:
        for k in e.keys():
            if k in {"ENTRYTYPE", "ID"} or k.startswith("__"):
                continue
            all_keys.add(k)

    for k in sorted(all_keys):
        merged[k] = _pick_field_value([e.get(k, "") for e in entries])

    # Keep provenance.
    merged["__sources"] = [
        {"path": e.get("__source_path"), "key": e.get("ID"), "entrytype": e.get("ENTRYTYPE")}
        for e in entries
    ]

    return merged


def canonical_id(entry: dict) -> str:
    doi = (entry.get("doi") or entry.get("DOI") or "").strip()
    if doi:
        return f"doi:{normalize_doi(doi)}"

    title = entry.get("title") or entry.get("TITLE")
    year = parse_year(entry)
    author_last = first_author_lastname(entry.get("author") or entry.get("AUTHOR"))

    if title:
        t = normalize_title(title)
        y = year or "????"
        a = author_last or "unknown"
        return f"tya:{t}|{y}|{a}"

    # Last resort: entry key.
    return f"key:{(entry.get('ID') or '').strip().lower()}"


def _ensure_unique_ids(entries: list[dict]) -> list[dict]:
    seen: dict[str, int] = {}
    out: list[dict] = []

    for entry in entries:
        base = (entry.get("ID") or "").strip() or "entry"
        n = seen.get(base, 0)
        if n == 0:
            entry["ID"] = base
        else:
            entry["ID"] = f"{base}_{n+1}"
        seen[base] = n + 1
        out.append(entry)

    return out


def deduplicate(entries: Iterable[dict], config: Optional[DedupConfig] = None) -> DedupResult:
    config = config or DedupConfig()

    groups: dict[str, list[dict]] = {}
    ordered_ids: list[str] = []

    for entry in entries:
        cid = canonical_id(entry)
        if cid not in groups:
            groups[cid] = []
            ordered_ids.append(cid)
        groups[cid].append(entry)

    unique_entries: list[dict] = []
    duplicate_groups: list[DuplicateGroup] = []

    for cid in ordered_ids:
        bucket = groups[cid]
        if len(bucket) == 1:
            unique_entries.append(dict(bucket[0]))
            continue

        if config.prefer_citekey == "first":
            kept = bucket[0]
        else:
            kept = _pick_best_entry(bucket)

        merged = merge_entries(bucket, prefer_citekey=config.prefer_citekey)
        unique_entries.append(merged)
        duplicate_groups.append(
            DuplicateGroup(
                canonical_id=cid,
                kept_entry_id=str(kept.get("ID") or ""),
                kept_source_path=kept.get("__source_path"),
                entries=[dict(e) for e in bucket],
            )
        )

    unique_entries = _ensure_unique_ids(unique_entries)
    return DedupResult(unique_entries=unique_entries, duplicate_groups=duplicate_groups)
