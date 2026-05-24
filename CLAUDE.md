# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

Converts GEDCOM genealogy files (from tools like Ancestry.com and Family Tree Maker) into structured JSON. Designed for large files (tested with 161K+ lines) and LLM-based genealogy queries.

## Running and testing

No external dependencies - pure Python 3.8+ standard library only.

```bash
# Run the parser
python main.py                          # parse default GEDCOM file
python main.py data/your_file.ged       # parse specific file
python main.py --stats-only             # statistics only
python main.py --search "John Doe"      # search by name

# Run tests
python -m unittest tests.test_parser -v
```

No `pyproject.toml`, `Makefile`, or linting configuration exists. Tests use `unittest`.

## Architecture

Two classes in `src/gedcom_parser.py`:

**`GEDCOMParser`** - Parses GEDCOM files via a line-by-line state machine:
- `parse()` - orchestrates the pipeline
- `_extract_individuals()` / `_extract_families()` - iterate level-0 records and collect fields at levels 1 and 2
- `_resolve_relationships()` - cross-links individuals and families after parsing

**`GenealogyQueryEngine`** - Query layer over parsed data:
- `find_person(name)` - case-insensitive substring search
- `get_family_tree(id, generations)` - recursive multi-generational tree
- `search_by_location(location)` - filter by birth/death place
- `get_statistics()` - summary counts by gender, century, occupation

`main.py` wires CLI arguments to these two classes.

## Data model

Individual records: `id`, `name`, `gender`, `birth`/`death` (each with `date` + `place`), `occupation`, `notes`, `parents`, `spouse`, `children`.

Family records: `id`, `marriage` (date + place), `husband_id`, `wife_id`, `children` (list of ids), `divorced`.

GEDCOM name format (`Firstname /SURNAME/`) is normalized to clean strings during extraction.

## Test data

Tests default to `data/Arbre_31_08_2025.ged` (user's actual family file, not in repo). `data/sample.ged` is a small synthetic file (4 individuals, 1 family) safe for isolated unit tests.
