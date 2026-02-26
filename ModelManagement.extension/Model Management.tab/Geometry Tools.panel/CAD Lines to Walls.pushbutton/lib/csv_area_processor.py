import csv
import os
from typing import List, Dict

def separate_by_floors(csv_path: str, area_column: str, floors_column: str,
                        out_single: str, out_multi: str) -> None:
    """Read ``csv_path`` and split rows according to number of floors.

    Rows with value 1 in ``floors_column`` are written to ``out_single``.
    Rows with value greater than 1 are written to ``out_multi``.
    ``area_column`` is preserved so the built area can be analysed later.
    """
    single: List[Dict[str, str]] = []
    multi: List[Dict[str, str]] = []

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            floors_raw = row.get(floors_column, '').strip()
            try:
                floors = int(floors_raw)
            except ValueError:
                continue
            if floors <= 1:
                single.append(row)
            else:
                multi.append(row)

    if single:
        _write_rows(out_single, single)
    if multi:
        _write_rows(out_multi, multi)


def _write_rows(path: str, rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def find_dwgs(base_dir: str, identifier: str) -> List[str]:
    """Search ``base_dir`` recursively for DWG files containing ``identifier``.

    Parameters
    ----------
    base_dir: str
        Directory to search.
    identifier: str
        Substring (code or name) to look for in file names.

    Returns
    -------
    list of str
        Paths of matching DWG files.
    """
    matches: List[str] = []
    for root, _, files in os.walk(base_dir):
        for fname in files:
            if fname.lower().endswith('.dwg') and identifier.lower() in fname.lower():
                matches.append(os.path.join(root, fname))
    return matches
