# encoding: utf-8

import _snippets as sn

import Autodesk.Revit.DB as db

import Autodesk.Revit.UI as ui

import os

import csv

from pyrevit import forms

__title__  = "Auditor"
__author__ = 'hadassa.lima@ufpe.br'

c = sn.ElementCollections()


def chose_ref_level():
    levels_data = [(level.get_Parameter(db.BuiltInParameter.DATUM_TEXT).AsString(), level.Elevation, level.Id) for level in c.levels]
    levels_ordered_by_elevation_ascending = sn.order_list(levels_data, 1)
    levels_names = [name for name, elevation, id in levels_ordered_by_elevation_ascending]
    # user choses by name, selected returns level id:
    selected = forms.CommandSwitchWindow.show(levels_names, message='Select a level')
    if not selected:
        return None
    return selected

selected_level_name = chose_ref_level()

''' based on users seleccted level
1 - filter rooms of that level
2 - compare list with rooms reference list from xlsx or csv
'''
rooms = []


def get_rooms_by_level(ref_level):
    for room in c.rooms:
        room_name = sn.get_name(room)
        room_level_name = room.get_Parameter(db.BuiltInParameter.LEVEL_NAME).AsString()
        room_number = room.get_Parameter(db.BuiltInParameter.ROOM_NUMBER).AsString()
        room_name_capitalized = sn.capitalize_first_word(room_name)
        if sn.values_match(room_level_name, ref_level):
            rooms.append(
                (room_number, room_name_capitalized)
                )
get_rooms_by_level(selected_level_name)
rooms_ordered = sn.order_list(rooms, 0)

# compare ordered list with list from reference building data file:
file_path = os.path.join(os.path.expanduser("~"), "Desktop", "rooms_list.csv")
# file_path_source = os.path.join(os.path.expanduser("~"), "Desktop", "CFCH_AREAS_2020.csv")
csv_path = 'C:\Users\Administrator\Documents\CB SEDE BLOCO C (ÁREAS) - JUN 2020.xlsx - GERAL.csv'
from pyrevit import script
csv = script.load_csv(csv_path)
print(csv[2:5])
# with open(file_path, mode='w') as file:
#     writer = csv.writer(file)
#     writer.writerow(["Number", "Name"])
#     writer.writerows(rooms_list)
#     os.startfile(file_path)
# with open(file_path_source) as csvfile:
#     spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
#     for row in spamreader:
#         print(row)s