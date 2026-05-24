#!/usr/bin/env python3
import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from gedcom_parser import GEDCOMParser, GenealogyQueryEngine

SAMPLE = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample.ged')


class TestGEDCOMParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = GEDCOMParser(SAMPLE).parse()
        cls.engine = GenealogyQueryEngine(cls.data)

    def test_individual_count(self):
        self.assertEqual(len(self.data['individuals']), 4)

    def test_family_count(self):
        self.assertEqual(len(self.data['families']), 2)

    def test_name_parsing(self):
        # "John /Smith/" -> "John Smith"
        self.assertEqual(self.data['individuals']['I1']['name'], 'John Smith')

    def test_birth(self):
        birth = self.data['individuals']['I1']['birth']
        self.assertEqual(birth['date'], '15 JAN 1900')
        self.assertEqual(birth['place'], 'New York, USA')

    def test_gender(self):
        self.assertEqual(self.data['individuals']['I1']['gender'], 'M')
        self.assertEqual(self.data['individuals']['I2']['gender'], 'F')

    def test_occupation(self):
        self.assertEqual(self.data['individuals']['I1']['occupation'], 'Engineer')

    def test_parents_resolved(self):
        # Robert (I3) is child of John (I1) and Mary (I2)
        parents = self.data['individuals']['I3']['parents']
        self.assertIn('I1', parents)
        self.assertIn('I2', parents)

    def test_spouse_resolved(self):
        self.assertIn('I2', self.data['individuals']['I1']['spouse'])
        self.assertIn('I1', self.data['individuals']['I2']['spouse'])

    def test_children_resolved(self):
        self.assertIn('I3', self.data['individuals']['I1']['children'])

    def test_find_person(self):
        results = self.engine.find_person('Smith')
        names = {p['name'] for p in results}
        self.assertIn('John Smith', names)
        self.assertIn('Robert Smith', names)

    def test_find_person_case_insensitive(self):
        self.assertEqual(
            len(self.engine.find_person('smith')),
            len(self.engine.find_person('Smith')),
        )

    def test_search_by_location(self):
        results = self.engine.search_by_location('New York')
        names = {p['name'] for p in results}
        self.assertIn('John Smith', names)

    def test_get_person_details(self):
        details = self.engine.get_person_details('I1')
        self.assertIn('Mary Johnson', details['spouse_names'])
        self.assertIn('Robert Smith', details['children_names'])

    def test_statistics(self):
        stats = self.engine.get_statistics()
        self.assertEqual(stats['total_individuals'], 4)
        self.assertEqual(stats['gender_distribution']['M'], 2)
        self.assertEqual(stats['gender_distribution']['F'], 2)

    def test_get_family_tree(self):
        tree = self.engine.get_family_tree('I3', generations=2)
        self.assertEqual(tree['name'], 'Robert Smith')
        parent_names = {p['name'] for p in tree.get('parents', [])}
        self.assertIn('John Smith', parent_names)


if __name__ == '__main__':
    unittest.main()
