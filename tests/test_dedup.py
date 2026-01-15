from __future__ import annotations

from pathlib import Path

from bib_dedup.bibtex_io import read_bib_files
from bib_dedup.dedup import DedupConfig, deduplicate


def test_dedup_by_doi(tmp_path: Path) -> None:
    a = tmp_path / "a.bib"
    b = tmp_path / "b.bib"

    a.write_text(
        """@article{KeyA,\n  title={A Paper},\n  doi={10.1000/XYZ},\n  year={2020}\n}\n""",
        encoding="utf-8",
    )
    b.write_text(
        """@article{KeyB,\n  title={A Paper (duplicate)},\n  doi={https://doi.org/10.1000/xyz},\n  year={2020},\n  url={https://example.com}\n}\n""",
        encoding="utf-8",
    )

    entries = read_bib_files([a, b])
    result = deduplicate(entries, DedupConfig(prefer_citekey="best"))

    assert len(result.unique_entries) == 1
    assert len(result.duplicate_groups) == 1
    merged = result.unique_entries[0]
    assert merged.get("doi").lower().endswith("10.1000/xyz")
    assert merged.get("url") == "https://example.com"


def test_dedup_by_title_year_author(tmp_path: Path) -> None:
    a = tmp_path / "a.bib"
    b = tmp_path / "b.bib"

    a.write_text(
        """@inproceedings{K1,\n  title={Deep {L}earning for Cats},\n  author={Smith, John and Doe, Jane},\n  year={2019}\n}\n""",
        encoding="utf-8",
    )
    b.write_text(
        """@inproceedings{K2,\n  title={Deep Learning for Cats},\n  author={John Smith and Jane Doe},\n  year={2019},\n  booktitle={CatConf}\n}\n""",
        encoding="utf-8",
    )

    entries = read_bib_files([a, b])
    result = deduplicate(entries)

    assert len(result.unique_entries) == 1
    merged = result.unique_entries[0]
    assert merged.get("booktitle") == "CatConf"
