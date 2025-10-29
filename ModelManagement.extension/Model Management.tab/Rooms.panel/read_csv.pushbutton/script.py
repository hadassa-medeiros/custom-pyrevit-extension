# -*- coding: utf-8 -*-
import os, csv
from pyrevit import forms, script
import _snippets as sn

csv_path = sn.pick_csv()
new_csv_file_path = 'C:\\Users\\Administrator\\new.csv'

def collect_room_data_from_file_rows(rows):
    rooms_from_csv = [()]

    for r in rows:
        try:
            if int(r[0]):
                rooms_from_csv.append(r)
            string_to_possibly_normalize = r[1]
            weird_chars = {'\xc3\xb3': 'aaaaa'}
            if 'a' in string_to_possibly_normalize:
                string_normalized = string_to_possibly_normalize.split('').replace(weird_chars['\xc3\xb3'])
                print(string_normalized)                
        except ValueError:
            pass
    # script.dump_csv(rooms_from_csv, new_csv_file_path)
    # os.startfile(new_csv_file_path)


if not csv_path:
    forms.alert('Nenhum arquivo selecionado.', warn_icon=True)
else:
    rows = sn.read_csv_rows(csv_path)
    collect_room_data_from_file_rows(rows)
    # forms.alert('OK! Linhas lidas: {}\nDelimitador: "{}"'.format(len(rows), delim))