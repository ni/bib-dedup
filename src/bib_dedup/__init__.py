"""bib-dedup: deduplicate and merge BibTeX files."""

from .dedup import DedupConfig, DedupResult, deduplicate
from .bibtex_io import read_bib_files, write_bib_file

__all__ = [
    "DedupConfig",
    "DedupResult",
    "deduplicate",
    "read_bib_files",
    "write_bib_file",
]
