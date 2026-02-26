import os
import csv
import tempfile
import unittest

from lib.csv_area_processor import separate_by_floors, find_dwgs


class TestCSVAProcessor(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.csv_path = os.path.join(self.tempdir.name, 'data.csv')
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['codigo', 'nome', 'area', 'pavimentos'])
            writer.writeheader()
            writer.writerows([
                {'codigo': '001', 'nome': 'Ed1', 'area': '100', 'pavimentos': '1'},
                {'codigo': '002', 'nome': 'Ed2', 'area': '200', 'pavimentos': '2'},
                {'codigo': '003', 'nome': 'Ed3', 'area': '150', 'pavimentos': '1'},
            ])

    def tearDown(self):
        self.tempdir.cleanup()

    def test_separate_by_floors(self):
        out_single = os.path.join(self.tempdir.name, 'single.csv')
        out_multi = os.path.join(self.tempdir.name, 'multi.csv')
        separate_by_floors(self.csv_path, 'area', 'pavimentos', out_single, out_multi)

        with open(out_single, newline='', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 2)

        with open(out_multi, newline='', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 1)

    def test_find_dwgs(self):
        base_dir = self.tempdir.name
        os.makedirs(base_dir, exist_ok=True)
        with open(os.path.join(base_dir, '001_example.dwg'), 'w'):
            pass
        with open(os.path.join(base_dir, 'other.txt'), 'w'):
            pass
        matches = find_dwgs(base_dir, '001')
        self.assertEqual(len(matches), 1)


if __name__ == '__main__':
    unittest.main()
