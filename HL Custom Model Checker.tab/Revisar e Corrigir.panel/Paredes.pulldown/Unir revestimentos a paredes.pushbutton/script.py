# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from revit_doc_interface import (RevitDocInterface, get_name)
from pyrevit import forms


interface = RevitDocInterface()

__title__     = "Unir revestimentos a paredes"
__author__    = "Hadassa Medeiros"
doc = __revit__.ActiveUIDocument.Document


def join_geometry(doc):
    # Inicia uma única transação para todas as alterações

    t = DB.Transaction(doc, "Join cutting solids")
    t.Start()

    try:
        for wall in interface.walls:
            # Obtém a geometria do elemento
            wall_geometry_obj = wall.get_Geometry(DB.Options())[0]
            # print(wall.Id, wall.Name)
            print(wall_geometry_obj)
            
            # # Itera sobre todos os objetos geométricos do elemento
            # for wall_geometry_obj in wall_geometry:
            #     if isinstance(wall_geometry_obj, DB.Solid) and wall_geometry_obj.Volume > 0:
            #         for elem_B in elements_B:
            #             elem_B_geometry = elem_B.get_Geometry(DB.Options())
                        
            #             for elem_B_geometry_object in elem_B_geometry:
            #                 if isinstance(elem_B_geometry_object, DB.Solid) and elem_B_geometry_object.Volume > 0:
            #                     intersection = DB.BooleanOperationsUtils.ExecuteBooleanOperation(
            #                         wall_geometry_obj, 
            #                         elem_B_geometry_object, 
            #                         DB.BooleanOperationsType.Intersect
            #                         )
            #                     if intersection and intersection.Volume > 0:
            #                         try:
            #                             DB.JoinGeometryUtils.JoinGeometry(doc, wall, elem_B)
            #                             print("Elementos unidos: {} (ID {}) + {} (ID {})".format(wall.Name, wall.Id, elem_B.Name, elem_B.Id))
            #                         except Exception as e:
            #                             print("Erro ao unir geometria: {}".format(e))
    except Exception as e:
        print("Erro geral na transação: {}".format(e))
    finally:
        # Comita a transação ao final
        t.Commit()

# chama a funcao para performar o batch join
join_geometry(doc, selected_category_A, selected_category_B)