# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import FilteredElementCollector, SpatialElement
import Autodesk.Revit.DB as DB
import csv
import codecs
doc = __revit__.ActiveUIDocument.Document

# Lê o arquivo CSV
def read_csv(file_path):
    with codecs.open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        return [row for row in csv_reader]

# Coleta os ambientes do modelo
def get_model_rooms(doc):
    collector = FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms)
    room_elements_list = collector.ToElements()
    return room_elements_list
    # return [room.LookupParameter("Name").AsString() for room in collector if room.Category.Name == "Rooms"]

def get_model_room_numbers(room_elements_list):
    return [room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsValueString() for room in room_elements_list]

def get_model_room_names(room_elements_list):
    return [room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsValueString() for room in room_elements_list]
def myFunc(e):
  return e['Number']

def model_room_infos(room_elements_list):
    all_rooms_info = []
    for room in room_elements_list:
        name = room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsValueString()
        number = int(room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsValueString())
        area = room.get_Parameter(DB.BuiltInParameter.ROOM_AREA).AsValueString().split('m')[0].split(' ')[0]
        room_info = {
            'Number': number,
            'Name': name,
            'Area': area
            }
        all_rooms_info.append(room_info)
    # all_rooms_info = all_rooms_info
    return all_rooms_info

# Caminho para o CSV
csv_file_path = "C:/Users/Hadassa/Documents/UFPE-SPO-CCBI/CCS Bloco F/Planilha_CCS_Bloco_F_Areas.csv"

# Comparação
csv_rooms = read_csv(csv_file_path)
model_rooms = get_model_rooms(doc)
# print(get_model_room_numbers(model_rooms))
print(model_room_infos(model_rooms).sort(key=myFunc))

headers = []
rooms_Terreo = []
rooms_floor1 = []
rooms_floor2 = []

for row in csv_rooms:
    # print(row[0])
    if 'AMBIENTE' in row[0]:
        i = csv_rooms.index(row)
        headers.append(i)
    
rooms_Terreo_index = range(headers[0]+1, headers[1])
rooms_floor1_indexes = range(headers[1]+1, headers[2])

for i in rooms_Terreo_index:
    room_Terreo_info = csv_rooms[i]
    r_number = room_Terreo_info[0]
    r_name = room_Terreo_info[1]
    r_area = room_Terreo_info[2]
    room_info = {
        'Number': r_number,
        'Name': r_name,
        'Area': r_area
        }
    print(room_info)



missing_in_model = [room for room in csv_rooms if room not in model_rooms]

# print("Faltando no modelo:", missing_in_model)