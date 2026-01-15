from __future__ import annotations

import re
import unicodedata
from typing import Optional


_DOI_PREFIX_RE = re.compile(r"^(https?://(dx\.)?doi\.org/|doi:)\s*", re.IGNORECASE)


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_doi(raw: str) -> str:
    value = normalize_whitespace(raw)
    value = _DOI_PREFIX_RE.sub("", value)
    value = value.strip().strip(".")
    return value.lower()


_LATEX_CMD_RE = re.compile(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?")


def _strip_latex(value: str) -> str:
    # Heuristic removal of common LaTeX markup; not a full parser.
    value = value.replace("{", "").replace("}", "")
    value = _LATEX_CMD_RE.sub(" ", value)
    return value


def normalize_title(raw: str) -> str:
    value = normalize_whitespace(raw)
    value = _strip_latex(value)
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return normalize_whitespace(value)


def parse_year(fields: dict) -> Optional[str]:
    year = (fields.get("year") or "").strip()
    if re.fullmatch(r"\d{4}", year):
        return year

    date = (fields.get("date") or "").strip()
    m = re.match(r"^(\d{4})", date)
    if m:
        return m.group(1)
    return None


def first_author_lastname(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None

    # Split on ' and ' per BibTeX author list.
    first = raw.split(" and ", 1)[0].strip()
    if not first:
        return None

    # Common BibTeX formats: 'Last, First' or 'First Last'
    if "," in first:
        last = first.split(",", 1)[0].strip()
    else:
        parts = [p for p in first.split() if p]
        last = parts[-1] if parts else ""

    last = unicodedata.normalize("NFKD", last)
    last = "".join(ch for ch in last if not unicodedata.combining(ch))
    last = re.sub(r"[^A-Za-z0-9]+", "", last)
    last = last.lower().strip()
    return last or None
