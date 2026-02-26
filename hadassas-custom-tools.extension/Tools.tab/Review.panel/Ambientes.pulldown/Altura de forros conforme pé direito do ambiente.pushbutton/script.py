# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from revit_doc_interface import (RevitDocInterface, GetCeilingHeight, ModelLine, find_id_by_element_name, get_name, get_names, metric_to_double, double_to_metric)

__title__     = "Create ceiling elements and set ceiling height"
__author__    = "Hadassa Medeiros"

doc = __revit__.ActiveUIDocument.Document
interface = RevitDocInterface()

all_rooms = interface.rooms

for i in interface.ceiling_types:
    print(i)
for room in all_rooms:
    ceiling_height = GetCeilingHeight(room)
    ceiling_type_id = interface.ceiling_types[0].Id
    level_id = room.LevelId

    first = DB.XYZ(0, 0, 0)
    second = DB.XYZ(20, 0, 0)
    third =  DB.XYZ(20, 15, 0)
    fourth =  DB.XYZ(0, 15, 0)

    profile = DB.CurveLoop()

    profile.Append(DB.Line.CreateBound(first, second))
    profile.Append(DB.Line.CreateBound(second, third))
    profile.Append(DB.Line.CreateBound(third, fourth))
    profile.Append(DB.Line.CreateBound(fourth, first))

    try:
        # Verifica as condições para criar o forro
        if ceiling_height is not None:
            print("Criando forro para ambiente {}".format(get_name(room)))

            # Inicia uma transação para criar o forro
            t = DB.Transaction(doc, "Create new ceiling instance")
            t.Start()

            # Cria o forro
            ceiling = DB.Ceiling.Create(doc, [profile], ceiling_type_id, level_id)

            # Define o parâmetro de altura do forro acima do nível
            param = ceiling.get_Parameter(DB.BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM)
            param.Set(ceiling_height)  # Define a altura (em metros)

            t.Commit()
    except Exception as e:
        print("Error creating wall instance: {}".format(e))
        pass

# conferir se há ambientes não colocados (área 0.00m2) e se estão na fase criada Levantamento e não possuem valor para fase demolida
# for room in all_rooms:
#     if room.Area == 0:
#         print('{} - {}  - {}'.format(
#             get_name(room), 
#             room.CreatedPhaseId,
#             room.Area
#             )
#         )
