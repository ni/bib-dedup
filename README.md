# bib-dedup

A small Python CLI to read multiple BibTeX (`.bib`) files, identify duplicate entries, and write one output BibTeX file that is the unique union of the inputs.

## Install (editable)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

Alternatively (one command):

```bash
make install-dev
```

## Usage

```bash
bib-dedup input1.bib input2.bib -o merged.bib
```

If you don’t want to activate the venv, you can also run:

```bash
.venv/bin/bib-dedup input1.bib input2.bib -o merged.bib
```

Optional JSON report:

```bash
bib-dedup input1.bib input2.bib -o merged.bib --report report.json
```

The report includes an `excluded_entries` list containing:
- duplicate input entries that were dropped in favor of a single merged entry
- any invalid/ignored records encountered while parsing

## Dedup strategy

- Primary: normalized DOI (if present)
- Fallback: normalized title + year + first-author last name

Within a duplicate group, entries are merged by taking the union of fields and preferring “better” values (non-empty / longer / more specific).
