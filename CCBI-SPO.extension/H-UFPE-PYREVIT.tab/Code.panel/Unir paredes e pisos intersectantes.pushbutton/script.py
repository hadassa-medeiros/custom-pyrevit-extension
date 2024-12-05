# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
import Autodesk.Revit.UI as UI

from revit_doc_interface import (RevitDocInterface, get_element, get_name, get_names, get_ids_of)
from pyrevit import forms

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

collect = DB.FilteredElementCollector(doc)

interface = RevitDocInterface()
selected_wall_elements = forms.SelectFromList.show(interface.walls, button_name='Select', multiselect=True)

# Define a transação
def join_geometry(doc, selected_wall_elements):
    # Inicia uma única transação para todas as alterações
    t = DB.Transaction(doc, "Join cutting solids")
    t.Start()

    try:
        # Para cada parede selecionada
        for selected_wall_element in selected_wall_elements:
            # Obtém a geometria da parede
            wall_geometry = selected_wall_element.get_Geometry(DB.Options())

            # Itera sobre todos os objetos geométricos da parede
            for geom_obj in wall_geometry:
                if isinstance(geom_obj, DB.Solid) and geom_obj.Volume > 0:
                    # Para cada piso, verifique a geometria
                    for floor in interface.floor_elements:
                        # Obtém a geometria do piso
                        floor_geometry = floor.get_Geometry(DB.Options())
                        
                        for floor_geom_obj in floor_geometry:
                            if isinstance(floor_geom_obj, DB.Solid) and floor_geom_obj.Volume > 0:
                                # Verifique se há interseção entre a parede e o piso
                                intersection = DB.BooleanOperationsUtils.ExecuteBooleanOperation(geom_obj, floor_geom_obj, DB.BooleanOperationsType.Intersect)
                                print(intersection.Volume)
                                if intersection and intersection.Volume > 0:  # Verifica se a interseção tem volume
                                    # Tenta realizar a união das geometrias
                                    try:
                                        DB.JoinGeometryUtils.JoinGeometry(doc, selected_wall_element, floor)
                                        print("Elementos unidos: Parede {} e Piso {}".format(get_name(selected_wall_element), get_name(floor)))
                                    except Exception as e:
                                        print("Erro ao unir geometria: {}".format(e))

    except Exception as e:
        print("Erro geral na transação: {}".format(e))
    finally:
        # Comita a transação ao final
        t.Commit()

# Exemplo de uso
join_geometry(doc, selected_wall_elements)


# if selected_wall_elements:
#     # Inicia uma única transação para todas as alterações
#     t = DB.Transaction(doc, "Join cutting solids")
#     t.Start()

#     try:
#         for selected_wall_element in selected_wall_elements:
#             # Obtém os sólidos de corte associados ao elemento
#             cutting_solids_elementIds_list = DB.SolidSolidCutUtils.GetCuttingSolids(selected_wall_element)

#             print(cutting_solids_elementIds_list)
#             for cutting_solid_id in cutting_solids_elementIds_list:
#                 cutting_solid = DB.Document.GetElement(doc, cutting_solid_id)
#                 print(DB.JoinGeometryUtils.IsCuttingElementInJoin(doc, cutting_solid, selected_wall_element))

#                 try:
#                     # Realiza a junção da geometria
#                     DB.JoinGeometryUtils.JoinGeometry(doc, selected_wall_element, cutting_solid)
#                 except Exception as e:
#                     print("Erro ao unir geometria: {}".format(e))
#     except Exception as e:
#         print("Erro geral na transação: {}".format(e))
#         # t.RollBack()
#     else:
#         t.Commit()