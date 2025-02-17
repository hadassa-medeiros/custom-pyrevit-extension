# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from revit_doc_interface import (RevitDocInterface, get_name)

interface = RevitDocInterface()

__title__     = "Unir paredes e pisos intersectantes"
__author__    = "Hadassa Medeiros"
doc = __revit__.ActiveUIDocument.Document

def join_geometry(doc, elements):
    # Inicia uma única transação para todas as alterações
    t = DB.Transaction(doc, "Join cutting solids")
    t.Start()

    try:
        for element in elements:
            # Obtém a geometria do elemento
            element_geometry = element.get_Geometry(DB.Options())

            # Itera sobre todos os objetos geométricos do elemento
            for geometry_object in element_geometry:
                if isinstance(geometry_object, DB.Solid) and geometry_object.Volume > 0:
                    for floor in interface.floors:
                        floor_geometry = floor.get_Geometry(DB.Options())
                        
                        for floor_geometry_object in floor_geometry:
                            if isinstance(floor_geometry_object, DB.Solid) and floor_geometry_object.Volume > 0:
                                intersection = DB.BooleanOperationsUtils.ExecuteBooleanOperation(
                                    geometry_object, 
                                    floor_geometry_object, 
                                    DB.BooleanOperationsType.Intersect
                                    )
                                if intersection and intersection.Volume > 0:
                                    try:
                                        DB.JoinGeometryUtils.JoinGeometry(doc, element, floor)
                                        print("Elementos unidos: Parede {} (ID {}) e Piso {} (ID {})".format(get_name(element), element.Id, get_name(floor), floor.Id))
                                    except Exception as e:
                                        print("Erro ao unir geometria: {}".format(e))

    except Exception as e:
        print("Erro geral na transação: {}".format(e))
    finally:
        # Comita a transação ao final
        t.Commit()

join_geometry(doc, interface.walls)