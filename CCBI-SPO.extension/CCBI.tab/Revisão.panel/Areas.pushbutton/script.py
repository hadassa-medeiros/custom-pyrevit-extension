# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
import csv
import codecs
import unicodedata

doc = __revit__.ActiveUIDocument.Document

# Função para normalizar strings
def normalize_string(s):
    if isinstance(s, str):
        return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("utf-8").strip()
    return s  # Caso não seja string, retorna sem alterações

# Lê o arquivo CSV e normaliza
def read_csv(file_path):
    with codecs.open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        # Normaliza todas as strings do CSV
        return [[normalize_string(cell) for cell in row] for row in csv_reader]

# Coleta os ambientes do modelo
def get_model_rooms(doc):
    collector = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms)
    room_elements_list = collector.ToElements()
    return room_elements_list
    # return [room.LookupParameter("Name").AsString() for room in collector if room.Category.Name == "Rooms"]

# def get_model_room_numbers(room_elements_list):
#     return [room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsValueString() for room in room_elements_list]

# def get_model_room_names(room_elements_list):
#     return [room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsValueString() for room in room_elements_list]
def myFunc(e):
  return e['Number']

# Coleta os ambientes do modelo e retorna suas informacoes basicas
def model_rooms_info(doc):
    collector = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms)
    room_elements_list = collector.ToElements()
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
# csv_file_path = "C:/Users/Hadassa/Documents/UFPE-SPO-CCBI/CCS Bloco F/Planilha_CCS_Bloco_F_Areas.csv"
csv_file_path = "C:/Users/Hadassa/Documents/UFPE-SPO-CCBI/CCEN Adm/CCEN_Administracao_Areas.csv"

csv_rooms = read_csv(csv_file_path)
model_rooms_data = sorted(model_rooms_info(doc), key=lambda x: x['Number'])

rooms_Terreo = []
rooms_floor1 = []
rooms_floor2 = []

keywords_of_final_sum_row = [' E ', ',', 'PAVIMENTOS']
# Inicialize a lista para armazenar os índices
start_end = []
# Percorra cada linha no CSV
for i, row in enumerate(csv_rooms):
    # level = 0
    # Se encontrar a palavra "AMBIENTE", começa o processamento
    if 'AMBIENTE' in row[0] and 'DENOMINACAO' in row[1]:
        # Capture o índice da primeira linha do nível
        first_row = i + 1  # A linha seguinte à linha "AMBIENTE"
        start_end.append(first_row)
    # Quando encontrar a linha com a contagem total por pavimento, capturar o indice da penultima linha (ultimo ambiente do pavimento em questao)
    elif 'TOTAL' in row[1] and all(keyword not in row[1] for keyword in keywords_of_final_sum_row):
        last_row = i - 1 # A penultima linha anterior à linha vazia
        start_end.append(last_row)
    #     rows_with_room_info = range(first_row, last_row)
print("Índices relevantes:", start_end)

rooms_by_level = {}
for i in range(len(start_end)):
    if i-1 < 0 or i % 2 == 0:
        pass
    else:
        lines = range(start_end[i-1], start_end[i])
        # print(lines)
        rooms_by_level[i//2] = lines
# print(rooms_by_level)
# print(len(rooms_by_level[0]), len(rooms_by_level[1]), len(rooms_by_level[2]))
def table_rooms_info_by_level(list_of_row_indexes):
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

def table_rooms_info(dict_of_row_indexes):
    # print(dict_of_row_indexes)
    all_rooms_info = []
    for v in dict_of_row_indexes.values():
        # rooms_info_by_level = []
        # print(v)
        for i in v:
            # print(i)
            row = csv_rooms[i]
            r_number = row[0]
            r_name = row[1]
            r_area = row[2]
            room_info = {
                'Number': r_number,
                'Name': r_name,
                'Area': r_area
                }
            # rooms_info_by_level.append(room_info)
            all_rooms_info.append(room_info)
    return all_rooms_info
# print(table_rooms_info_by_level(rooms_by_level[0]))
# print(table_rooms_info(rooms_by_level))
table_rooms_count = len(table_rooms_info(rooms_by_level))
model_rooms_count = len(model_rooms_data)

# conferir se quantidade total de ambientes é a mesma na tabela e no modelo
if table_rooms_count == model_rooms_count:
    print('A contagem total de ambientes corresponde.')
else:
    print(
        'Há diferenca de {} ambientes no modelo em relação à planilha!'
        .format(model_rooms_count - table_rooms_count)
    )

# Compare as salas que estão na tabela, mas não no modelo
table_rooms_data = table_rooms_info(rooms_by_level)

def normalize_room_info(room):
    return {
        'Number': int(room['Number']) if isinstance(room['Number'], str) else room['Number'],
        'Name': normalize_string(room['Name']).strip().upper(),
        'Area': float(room['Area']) if isinstance(room['Area'], str) else room['Area']
    }

# Normalize os dados antes de comparar
normalized_model_rooms = [normalize_room_info(room) for room in model_rooms_data]
normalized_table_rooms = [normalize_room_info(room) for room in table_rooms_data]

# print(normalized_model_rooms)
# print(normalized_table_rooms)

# Comparar cada informacao (numero, nome e area) das duas fontes e avisar se ha divergencias
for dict1, dict2 in zip(normalized_model_rooms, normalized_table_rooms):
    print(dict1['Number'], dict1['Name'], '{:.2f}'.format(dict1['Area']))
    if dict1["Name"] != dict2["Name"]:
        print("{} vs. {}".format(dict1["Name"], dict2["Name"]))
    elif dict1['Number'] != dict2['Number']:
        print(" {} vs. {}".format(dict1['Number'], dict2['Number']))
    elif dict1['Area'] != dict2['Area']:
        print(" {} vs. {}".format(dict1['Area'], dict2['Area']))
    else:
        print('Informacoes dos ambientes sao iguais')
    print('-----------------------------------')

        # print("Nomes dos ambientes equivalem: {} (modelo) != {} (planilha)".format(dict1, dict2))
# else:
#     print("Todos os ambientes da tabela estão presentes no modelo!")


#     # Compare each key and value
#     for key in model_rooms_data:
#         if key not in d2 or model_rooms_data[key] != d2[key]:
#             print(False)
#             break
#     else:
#         # This runs only if no mismatches are found
#         print(True)
