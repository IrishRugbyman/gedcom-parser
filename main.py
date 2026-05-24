#!/usr/bin/env python3
import sys
import os
import argparse
import json

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from gedcom_parser import GEDCOMParser, GenealogyQueryEngine


def main():
    parser = argparse.ArgumentParser(
        description="GEDCOM Genealogy Parser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # parse default GEDCOM file
  python main.py data/my_family.ged        # parse specific file
  python main.py --search "John Doe"       # search for a person
  python main.py --stats-only              # show only statistics
        """
    )
    parser.add_argument('gedcom_file', nargs='?', default='data/Arbre 31_08_2025.ged')
    parser.add_argument('--output', '-o', help='output JSON file path')
    parser.add_argument('--stats-only', action='store_true')
    parser.add_argument('--search', help='search for a person by name')
    args = parser.parse_args()

    if not os.path.exists(args.gedcom_file):
        print(f"Error: file '{args.gedcom_file}' not found", file=sys.stderr)
        sys.exit(1)

    data = GEDCOMParser(args.gedcom_file).parse()
    engine = GenealogyQueryEngine(data)
    stats = engine.get_statistics()

    print(f"Individuals: {stats['total_individuals']}")
    print(f"Families:    {stats['total_families']}")
    print(f"Living:      {stats['living_people']}")

    if args.search:
        results = engine.find_person(args.search)
        print(f"\nSearch '{args.search}': {len(results)} result(s)")
        for person in results[:10]:
            birth = person.get('birth', {}).get('date', '')
            suffix = f"  b. {birth}" if birth else ''
            print(f"  {person['name']} ({person['id']}){suffix}")
        if len(results) > 10:
            print(f"  ... and {len(results) - 10} more")

    if not args.stats_only:
        output_file = args.output or args.gedcom_file.replace('.ged', '_parsed.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"\nSaved to {output_file} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
