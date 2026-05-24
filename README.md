# GEDCOM Genealogy Parser

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Convert GEDCOM genealogy files to structured JSON for analysis and LLM querying.

## Requirements

- Python 3.8+
- No external dependencies

## Usage

```bash
python main.py                                    # parse default GEDCOM file
python main.py data/your_family.ged               # parse specific file
python main.py data/family.ged --output out.json  # custom output path
python main.py --stats-only                       # statistics only
python main.py --search "John Doe"                # search by name
```

Export a `.ged` file from your genealogy software (Ancestry, Family Tree Maker, etc.) and place it in `data/`.

## Output format

```json
{
  "individuals": {
    "I1": {
      "id": "I1",
      "name": "John Smith",
      "gender": "M",
      "birth": { "date": "15 JAN 1900", "place": "New York, USA" },
      "death": { "date": "12 MAR 1985", "place": "California, USA" },
      "occupation": "Engineer",
      "parents": ["I5", "I6"],
      "spouse": ["I2"],
      "children": ["I3", "I4"]
    }
  },
  "families": {
    "F1": {
      "id": "F1",
      "husband": "I1",
      "wife": "I2",
      "children": ["I3", "I4"],
      "marriage": { "date": "1925", "place": "Chicago, USA" }
    }
  }
}
```

## LLM integration

```python
import json
from src.gedcom_parser import GEDCOMParser, GenealogyQueryEngine

data = GEDCOMParser("data/family.ged").parse()
engine = GenealogyQueryEngine(data)

engine.find_person("Smith")
engine.get_family_tree("I1", generations=3)
engine.search_by_location("Paris")
engine.get_statistics()

# Or load a previously saved JSON
with open("data/family_parsed.json", encoding="utf-8") as f:
    family_data = json.load(f)
```

## Performance

Tested on a 161,606-line file: ~2 seconds, 13,109 individuals, 6,356 families.

## Tests

```bash
python -m unittest tests.test_parser -v
```

## License

MIT
