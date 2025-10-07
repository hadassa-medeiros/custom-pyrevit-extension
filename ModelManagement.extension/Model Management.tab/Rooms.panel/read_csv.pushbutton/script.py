# -*- coding: utf-8 -*-
import os, csv
from pyrevit import forms, script # pyright: ignore[reportMissingImports]
import _snippets as sn # pyright: ignore[reportMissingImports]

csv_path = sn.pick_csv()
new_csv_file_path = 'C:\\Users\\Administrator\\new.csv'

def collect_room_data_from_file_rows(rows):
    rooms_from_csv = [()]

    for r in rows:
        print(r)
        try:
            if int(r[0]):
                rooms_from_csv.append(r)
            if 'ó' in r[1]:
                print(r)
        except ValueError:
            pass
    script.dump_csv(rooms_from_csv, new_csv_file_path)
    os.startfile(new_csv_file_path)


if not csv_path:
    forms.alert('Nenhum arquivo selecionado.', warn_icon=True)
else:
    rows = sn.read_csv_rows(csv_path)
    collect_room_data_from_file_rows(rows)
    # forms.alert('OK! Linhas lidas: {}\nDelimitador: "{}"'.format(len(rows), delim))