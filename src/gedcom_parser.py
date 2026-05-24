#!/usr/bin/env python3
from datetime import datetime
from typing import Dict, List, Optional


class GEDCOMParser:
    def __init__(self, gedcom_file: str):
        self.gedcom_file = gedcom_file
        self.individuals: Dict = {}
        self.families: Dict = {}
        self._lines: List[str] = []

    def parse(self) -> Dict:
        with open(self.gedcom_file, 'r', encoding='utf-8') as f:
            self._lines = [line.strip() for line in f if line.strip()]
        self._extract_individuals()
        self._extract_families()
        self._resolve_relationships()
        return {
            "individuals": self.individuals,
            "families": self.families,
            "summary": {
                "total_individuals": len(self.individuals),
                "total_families": len(self.families),
                "parsed_at": datetime.now().isoformat(),
            },
        }

    @staticmethod
    def _parse_line(line: str):
        parts = line.split(' ', 2)
        if len(parts) < 2:
            return None, None, None
        try:
            level = int(parts[0])
        except ValueError:
            return None, None, None
        return level, parts[1], parts[2] if len(parts) > 2 else ''

    def _extract_individuals(self):
        current_id = None
        record: Dict = {}
        section = None

        for line in self._lines:
            level, tag, value = self._parse_line(line)
            if level is None:
                continue

            if level == 0:
                if current_id:
                    self.individuals[current_id] = record
                if value == 'INDI':
                    current_id = tag.strip('@')
                    record = {
                        'id': current_id,
                        'name': '',
                        'gender': '',
                        'birth': {},
                        'death': {},
                        'occupation': '',
                        'notes': [],
                        'families_as_child': [],
                        'families_as_spouse': [],
                        'media': [],
                    }
                else:
                    current_id = None
                section = None
                continue

            if current_id is None:
                continue

            if level == 1:
                section = None
                if tag == 'NAME':
                    # GEDCOM name format: "Firstname /SURNAME/" -> "Firstname SURNAME"
                    record['name'] = ' '.join(p.strip() for p in value.split('/') if p.strip())
                elif tag == 'SEX':
                    record['gender'] = value
                elif tag == 'OCCU':
                    record['occupation'] = value
                elif tag == 'BIRT':
                    section = 'birth'
                elif tag == 'DEAT':
                    section = 'death'
                elif tag == 'FAMC':
                    record['families_as_child'].append(value.strip('@'))
                elif tag == 'FAMS':
                    record['families_as_spouse'].append(value.strip('@'))
                elif tag == 'OBJE':
                    section = 'media'
                elif tag == 'NOTE':
                    section = 'notes'
                    if value:
                        record['notes'].append(value)

            elif level == 2 and section:
                if section in ('birth', 'death'):
                    if tag == 'DATE':
                        record[section]['date'] = value
                    elif tag == 'PLAC':
                        record[section]['place'] = value
                elif section == 'media' and tag == 'FILE':
                    record['media'].append(value)
                elif section == 'notes' and tag in ('CONT', 'CONC', 'NOTE') and value:
                    record['notes'].append(value)

        if current_id:
            self.individuals[current_id] = record

    def _extract_families(self):
        current_id = None
        record: Dict = {}
        section = None

        for line in self._lines:
            level, tag, value = self._parse_line(line)
            if level is None:
                continue

            if level == 0:
                if current_id:
                    self.families[current_id] = record
                if value == 'FAM':
                    current_id = tag.strip('@')
                    record = {
                        'id': current_id,
                        'marriage': {},
                        'husband': '',
                        'wife': '',
                        'children': [],
                        'notes': [],
                        'divorced': False,
                    }
                else:
                    current_id = None
                section = None
                continue

            if current_id is None:
                continue

            if level == 1:
                section = None
                if tag == 'HUSB':
                    record['husband'] = value.strip('@')
                elif tag == 'WIFE':
                    record['wife'] = value.strip('@')
                elif tag == 'CHIL':
                    record['children'].append(value.strip('@'))
                elif tag in ('DIV', 'SEP'):
                    record['divorced'] = True
                elif tag == 'MARR':
                    section = 'marriage'
                elif tag == 'NOTE' and value:
                    record['notes'].append(value)

            elif level == 2 and section == 'marriage':
                if tag == 'DATE':
                    record['marriage']['date'] = value
                elif tag == 'PLAC':
                    record['marriage']['place'] = value

        if current_id:
            self.families[current_id] = record

    def _resolve_relationships(self):
        for ind_id, person in self.individuals.items():
            person['parents'] = []
            person['spouse'] = []
            person['children'] = []

            for fam_id in person['families_as_child']:
                fam = self.families.get(fam_id, {})
                for role in ('husband', 'wife'):
                    if fam.get(role):
                        person['parents'].append(fam[role])

            for fam_id in person['families_as_spouse']:
                fam = self.families.get(fam_id, {})
                if fam.get('husband') == ind_id and fam.get('wife'):
                    person['spouse'].append(fam['wife'])
                elif fam.get('wife') == ind_id and fam.get('husband'):
                    person['spouse'].append(fam['husband'])
                person['children'].extend(fam.get('children', []))


class GenealogyQueryEngine:
    def __init__(self, data: Dict):
        self.individuals: Dict = data['individuals']
        self.families: Dict = data['families']

    def find_person(self, name_query: str) -> List[Dict]:
        query = name_query.lower()
        return [p for p in self.individuals.values() if query in p['name'].lower()]

    def get_person_details(self, person_id: str) -> Optional[Dict]:
        person = self.individuals.get(person_id)
        if not person:
            return None
        result = person.copy()
        result['parent_names'] = [self.individuals[p]['name'] for p in person['parents'] if p in self.individuals]
        result['spouse_names'] = [self.individuals[s]['name'] for s in person['spouse'] if s in self.individuals]
        result['children_names'] = [self.individuals[c]['name'] for c in person['children'] if c in self.individuals]
        return result

    def get_family_tree(self, person_id: str, generations: int = 3) -> Dict:
        visited: set = set()

        def build_tree(pid: str, depth: int) -> Dict:
            if depth == 0 or pid not in self.individuals or pid in visited:
                return {}
            visited.add(pid)
            person = self.individuals[pid]
            tree: Dict = {
                'id': pid,
                'name': person['name'],
                'birth': person['birth'],
                'death': person['death'],
            }
            if depth > 1:
                tree['parents'] = [t for par in person['parents'] if (t := build_tree(par, depth - 1))]
                tree['children'] = [t for chi in person['children'] if (t := build_tree(chi, depth - 1))]
            visited.discard(pid)
            return tree

        return build_tree(person_id, generations)

    def search_by_location(self, location: str) -> List[Dict]:
        query = location.lower()
        return [
            p for p in self.individuals.values()
            if query in p['birth'].get('place', '').lower()
            or query in p['death'].get('place', '').lower()
        ]

    def get_statistics(self) -> Dict:
        stats: Dict = {
            'total_individuals': len(self.individuals),
            'total_families': len(self.families),
            'gender_distribution': {'M': 0, 'F': 0, 'Unknown': 0},
            'occupation_distribution': {},
            'century_distribution': {},
            'living_people': 0,
        }

        for person in self.individuals.values():
            gender = person.get('gender') or 'Unknown'
            stats['gender_distribution'][gender if gender in ('M', 'F') else 'Unknown'] += 1

            occ = person.get('occupation', '')
            if occ:
                stats['occupation_distribution'][occ] = stats['occupation_distribution'].get(occ, 0) + 1

            birth_date = person['birth'].get('date', '')
            if birth_date and len(birth_date) >= 4:
                try:
                    year = int(birth_date[-4:])
                    label = f"{(year // 100) + 1}th century"
                    stats['century_distribution'][label] = stats['century_distribution'].get(label, 0) + 1
                except ValueError:
                    pass

            if not person['death'].get('date'):
                stats['living_people'] += 1

        return stats
