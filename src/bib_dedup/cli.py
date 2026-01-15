from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional

from .bibtex_io import read_bib_files_with_exclusions, write_bib_file
from .dedup import DedupConfig, deduplicate
from .report import write_report


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="bib-dedup",
        description="Deduplicate and merge multiple BibTeX files into one unique union.",
    )
    p.add_argument("inputs", nargs="+", help="Input .bib files")
    p.add_argument("-o", "--output", required=True, help="Output .bib file")
    p.add_argument(
        "--prefer-citekey",
        choices=["best", "first"],
        default="best",
        help="When merging duplicates, which citekey to keep.",
    )
    p.add_argument(
        "--report",
        default=None,
        help="Optional path to write a JSON report of duplicates.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write output; just print summary stats.",
    )
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    input_paths = [Path(p) for p in args.inputs]
    output_path = Path(args.output)
    report_path = Path(args.report) if args.report else None

    entries, excluded = read_bib_files_with_exclusions(input_paths)
    result = deduplicate(entries, DedupConfig(prefer_citekey=args.prefer_citekey))

    if args.dry_run:
        print(f"Read {len(entries)} entries from {len(input_paths)} files")
        print(f"Unique entries: {len(result.unique_entries)}")
        print(f"Duplicate groups: {len(result.duplicate_groups)}")
        return 0

    write_bib_file(output_path, result.unique_entries)

    if report_path:
        write_report(report_path, result, excluded=excluded)

    print(f"Wrote {len(result.unique_entries)} unique entries to {output_path}")
    if report_path:
        print(f"Wrote duplicate report to {report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
