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

# def get_model_room_numbers(room_elements_list):
#     return [room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsValueString() for room in room_elements_list]

# def get_model_room_names(room_elements_list):
#     return [room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsValueString() for room in room_elements_list]
def myFunc(e):
  return e['Number']

def model_rooms_info(room_elements_list):
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
model_rooms_dict = sorted(model_rooms_info(model_rooms), key=lambda x: x['Number'])

# print(model_rooms_dict)
print('----------------------------------')
headers = []
rooms_Terreo = []
rooms_floor1 = []
rooms_floor2 = []

# Inicialize a lista para armazenar os índices
start_end = []
# Percorra cada linha no CSV
for i, row in enumerate(csv_rooms):
    # level = 0
    # Se encontrar a palavra "AMBIENTE", começa o processamento
    if 'AMBIENTE' in row[0]:
        # Capture o índice da primeira linha do nível
        first_row = i + 1  # A linha seguinte à linha "AMBIENTE"
        start_end.append(first_row)  # Adiciona o índice inicial
    # Quando encontrar a linha com a contagem total por pavimento, capturar o indice da penultima linha (ultimo ambiente do pavimento em questao)
    elif 'TOTAL' in row[1] and ' E ' not in row[1]:
        last_row = i - 2 # A penultima linha anterior à linha vazia
        start_end.append(last_row)
    #     rows_with_room_info = range(first_row, last_row)

# Exibir os índices capturados
print("Índices relevantes:", start_end)

# for row in csv_rooms:
#     # print(row[0])
#     # gravar linhas imediatamente antes e imediatamente apos as linhas que contem informacoes de ambientes por nivel
#     i = csv_rooms.index(row)
#     start_end_terreo = []
#     if 'AMBIENTE' in row[0]:
#         first_row = i + 1
#         while row[0] != '' and row[0] != :
#             headers.append(i)
#         # print(headers)
#     # elif 'TOTAL' in row[1] and csv_rooms[i-2][1] != '':
#     #     last_row = i - 2
#     #     rows_with_room_info = range(first_row, last_row)
#     #     headers.append(rows_with_room_info)

print(headers)
def table_rooms_info(list_of_row_indexes):
    all_rooms_info = []

    for i in list_of_row_indexes:
        row = csv_rooms[i]
        r_number = row[0]
        r_name = row[1]
        r_area = row[2]
        room_info = {
            'Number': r_number,
            'Name': r_name,
            'Area': r_area
            }
        all_rooms_info.append(room_info)
    return all_rooms_info

# rows_rooms_terreo = range(headers[0]+1, headers[1])
# rows_rooms_floor1 = range(headers[1]+1, headers[2])
# rows_rooms_floor2 = range(headers[2]+1, 100)

# print(table_rooms_info(rows_rooms_terreo))
# print('---------------------------')
# print(table_rooms_info(rows_rooms_floor1))
# print('---------------------------')
# print(table_rooms_info(rows_rooms_floor2))
# print('---------------------------')
# for i in rooms_Terreo_index:
#     room_Terreo_info = csv_rooms[i]
#     r_number = room_Terreo_info[0]
#     r_name = room_Terreo_info[1]
#     r_area = room_Terreo_info[2]
#     room_info = {
#         'Number': r_number,
#         'Name': r_name,
#         'Area': r_area
#         }
#     print(room_info)
# Check if lengths are the same
# if len(model_rooms_dict) != len(d2):
#     print(False)
# else:
  
#     # Compare each key and value
#     for key in model_rooms_dict:
#         if key not in d2 or model_rooms_dict[key] != d2[key]:
#             print(False)
#             break
#     else:
      
#         # This runs only if no mismatches are found
#         print(True)


missing_in_model = [room for room in csv_rooms if room not in model_rooms]

# print("Faltando no modelo:", missing_in_model)