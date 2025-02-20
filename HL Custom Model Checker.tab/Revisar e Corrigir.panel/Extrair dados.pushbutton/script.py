# -*- coding: utf-8 -*-

import Autodesk.Revit.DB as DB
import json
import os
import codecs  # 🔥 Import necessário para compatibilidade com IronPython
from Autodesk.Revit.UI import TaskDialog
from revit_doc_interface import remove_acentos
from pyrevit import forms, script, revit, DB


#
import unicodedata
# from Autodesk.Revit.ApplicationServices import OpenSharedParameterFile

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
room_data = []

for room in rooms:
    try:
        # Obtém parâmetros e verifica se têm valor antes de acessá-los
        room_name = room.get_Parameter(DB.BuiltInParameter.ROOM_NAME)
        room_number = room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER)
        area = room.get_Parameter(DB.BuiltInParameter.ROOM_AREA)
        department = room.get_Parameter(DB.BuiltInParameter.ROOM_DEPARTMENT)
        finishes = room.get_Parameter(DB.SharedParameterElement)

        # Converte valores, tratando casos onde o parâmetro pode ser None
        room_name = room_name.AsString() if room_name and room_name.HasValue else "Sem Nome"
        room_number = room_number.AsString() if room_number and room_number.HasValue else "Sem Número"
        area_m2 = round(area.AsDouble() * 0.092903, 2) if area and area.HasValue else 0.0  # Converte pés² para m²
        department = department.AsString() if department and department.HasValue else "Desconhecido"

        # Adiciona os dados à lista
        room_data.append({
            "numero": room_number,
            "nome": room_name,
            "area": area_m2,
            "departamento": department
        })

    except Exception as e:
        print("Erro ao processar sala:", e)

building_data = {
    "nome_arquivo": doc.Title,
    "salas": room_data,
    "ultima_revisao": "2025-02-11",
    "arquivo_rvt": "https://drive.google.com/seu_arquivo_rvt"
}


output_folder = os.path.expanduser("~") + "/Documents/RevitExports"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
file_name = remove_acentos(doc.Title).split(' ')[0]

file_path = os.path.join(output_folder, '{}.json'.format(file_name))

with codecs.open(file_path, "w", "utf-8") as f:
    json.dump(building_data, f, indent=4, ensure_ascii=False)  # 🔥 ensure_ascii=False mantém caracteres especiais
    os.startfile(file_path)


TaskDialog.Show("Extração Concluída", "📌 Dados salvos em:\n{}".format(file_path))
