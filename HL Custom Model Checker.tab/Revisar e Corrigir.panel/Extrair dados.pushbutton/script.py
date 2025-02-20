# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
import json
import os
import codecs  # 🔥 Import necessário para compatibilidade com IronPython
from Autodesk.Revit.UI import TaskDialog
from revit_doc_interface import remove_acentos

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

# 🔎 Obtém todas as salas no modelo
rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
room_data = []

def normalize_param(param_obj):
    return param_obj.AsString() if param_obj and param_obj.HasValue else None

project_info_elem = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_ProjectInformation).FirstElement()
campus_or_center = normalize_param(project_info_elem.LookupParameter('NOME CAMPUS/CENTRO'))
project_info = DB.FilteredElementCollector(doc).OfClass(DB.ProjectInfo).FirstElement()
params = [param.Definition.Name for param in project_info.Parameters]
print(params)

for room in rooms:
    # Obtém parâmetros e verifica se têm valor antes de acessá-los
    room_name = normalize_param(room.get_Parameter(DB.BuiltInParameter.ROOM_NAME))
    room_number = normalize_param(room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER))
    area = room.get_Parameter(DB.BuiltInParameter.ROOM_AREA)
    department = normalize_param(room.get_Parameter(DB.BuiltInParameter.ROOM_DEPARTMENT))
    floor_finish = normalize_param(room.LookupParameter('Piso_REV_1'))
    wall_finish= normalize_param(room.LookupParameter('Parede_REV_1'))
    ceiling_finish = normalize_param(room.LookupParameter('Forro_REV_1'))
    room_use = normalize_param(room.LookupParameter('USO CLASSIFICACAO'))
    room_use_spiunet = normalize_param(room.LookupParameter('USO SPIUNET CLASSIFICACAO'))

    project_name = DB.ProjectInfo.Name
    # project_params = DB.ProjectInfo.LookupParameter
    # print(project_name)

    area_m2 = round(area.AsDouble() * 0.092903, 2) if area and area.HasValue else 0.0  # 🔄 Converte pés² para m²
    # print([i.Name for i in project_info_cat])
    try:
        # Adiciona os dados à lista
        room_data.append({
            "numero": room_number,
            "nome": room_name,
            "area": area_m2,
            "departamento": department,
            "campus/centro": campus_or_center,
            "revestimentos": {
                    "piso": floor_finish,
                    "parede": wall_finish,
                    "forro": ceiling_finish
                },
            "classificacao de uso": {
                "ccbi": room_use,
                "spiunet": room_use_spiunet
            }
        })

    except Exception as e:
        print("❌ Erro ao processar sala:", e)

# 🔎 Estrutura do JSON final
building_data = {
    "nome_arquivo": doc.Title,
    "salas": room_data,
    "ultima_revisao": "2025-02-11",
    "arquivo_rvt": "https://drive.google.com/seu_arquivo_rvt"
}

# 📂 Define o caminho de saída
output_folder = os.path.expanduser("~") + "/Documents/RevitExports"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 📌 Remove acentos e formata nome do arquivo corretamente
file_name = remove_acentos(doc.Title).replace(" ", "_")  # Substitui espaços por underscore
file_path = os.path.join(output_folder, "{}.json".format(file_name))

# 💾 Salva o JSON no arquivo
with codecs.open(file_path, "w", "utf-8") as f:
    json.dump(building_data, f, indent=4, ensure_ascii=False)
    os.startfile(file_path)

# 📢 Notifica o usuário

TaskDialog.Show("Extração Concluída", "📌 Dados salvos em:\n{}".format(file_path))
