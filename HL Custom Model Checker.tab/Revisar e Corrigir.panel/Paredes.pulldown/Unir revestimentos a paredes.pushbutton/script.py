# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from revit_doc_interface import (RevitDocInterface, get_name)
from pyrevit import forms


interface = RevitDocInterface()

__title__     = "Unir revestimentos a paredes"
__author__    = "Hadassa Medeiros"
doc = __revit__.ActiveUIDocument.Document


def join_geometry(doc, elem_list_A, elem_list_B):
    t = DB.Transaction(doc, "Join cutting solids")
    t.Start()

    try:
        for elem_A in elem_list_A:
            if 'REV' in elem_A.Name or len(
                elem_A.GetCompoundStructure().GetLayers()
            ) == 1:
            # Obtém a geometria do elemento
                elem_A_geometry = elem_A.get_Geometry(DB.Options())
                print(elem_A.Id, elem_A.Name)

    #         # Itera sobre todos os objetos geométricos do elemento
    #         for elem_A_geometry_object in elem_A_geometry:
    #             if isinstance(
    #                 elem_A_geometry_object, DB.Solid
    #             ) and elem_A_geometry_object.Volume > 0 and elem_B not in elem_A.GetJoinedElements():
    #                 for elem_B in elem_list_B:
    #                     if elem_A.Id != elem_B.Id:
    #                         elem_B_geometry = elem_B.get_Geometry(DB.Options())
                            
    #                         for elem_B_geometry_object in elem_B_geometry:
    #                             if isinstance(elem_B_geometry_object, DB.Solid) and elem_B_geometry_object.Volume > 0:
    #                                 try:
    #                                     DB.JoinGeometryUtils.JoinGeometry(doc, elem_A, elem_B)
    #                                     print("Elementos unidos: {} (ID {}) + {} (ID {})".format(elem_A.Name, elem_A.Id, elem_B.Name, elem_B.Id))
    #                                 except Exception as e:
    #                                     print("Erro ao unir geometria: {}".format(e))
    except Exception as e:
        print("Erro geral na transação: {}".format(e))
    # finally:
    #     # Comita a transação ao final
    #     t.Commit()

# chama a funcao para performar o batch join
join_geometry(doc, interface.walls, interface.walls)