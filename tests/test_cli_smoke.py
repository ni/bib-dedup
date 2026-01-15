from __future__ import annotations

from pathlib import Path

from bib_dedup.cli import main


def test_cli_smoke(tmp_path: Path) -> None:
    a = tmp_path / "a.bib"
    out = tmp_path / "out.bib"

    a.write_text(
        """@article{KeyA,\n  title={A Paper},\n  doi={10.1000/xyz},\n  year={2020}\n}\n""",
        encoding="utf-8",
    )

    code = main([str(a), "-o", str(out)])
    assert code == 0
    assert out.exists()
    assert "@article" in out.read_text(encoding="utf-8")


def test_cli_double_brace_titles_default(tmp_path: Path) -> None:
    a = tmp_path / "a.bib"
    out = tmp_path / "out.bib"

    a.write_text(
        """@article{KeyA,\n  title={Deep Learning for Cats},\n  year={2020}\n}\n""",
        encoding="utf-8",
    )

    code = main([str(a), "-o", str(out)])
    assert code == 0
    text = out.read_text(encoding="utf-8")
    assert "title = {{Deep Learning for Cats}}" in text


def test_cli_no_double_brace_titles_flag(tmp_path: Path) -> None:
    a = tmp_path / "a.bib"
    out = tmp_path / "out.bib"

    a.write_text(
        """@article{KeyA,\n  title={Deep Learning for Cats},\n  year={2020}\n}\n""",
        encoding="utf-8",
    )

    code = main([str(a), "-o", str(out), "--no-double-brace-titles"])
    assert code == 0
    text = out.read_text(encoding="utf-8")
    assert "title = {{Deep Learning for Cats}}" not in text
    assert "title = {Deep Learning for Cats}" in text
