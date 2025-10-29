# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from pyrevit import forms
from revit_doc_interface import (RevitDocInterface, get_name)
import _snippets as sn


interface = RevitDocInterface()

__title__     = "Batch Join Geometry"
__annotations__ = "Une elementos de duas categorias selecionadas que possuem geometria intersectante."
__author__    = "Hadassa Medeiros"

doc = __revit__.ActiveUIDocument.Document


def get_category_name(category_enum):
    category_name = category_enum.ToString()
    return str(category_name.strip("OST_"))

walls = "Paredes"
floors = "Pisos"
beams = "Vigas"
ceilings = "Forros"
columns = "Colunas Arquitetônicas"
struct_columns = "Colunas Estruturais"

'''
walls = get_category_name(DB.BuiltInCategory.OST_Walls)
floors = get_category_name(DB.BuiltInCategory.OST_Floors)
beams = get_category_name(DB.BuiltInCategory.OST_StructuralFraming)
ceilings = get_category_name(DB.BuiltInCategory.OST_Ceilings)
columns = get_category_name(DB.BuiltInCategory.OST_Columns)
'''

category_names_and_elements = {
    walls: interface.walls,
    floors: interface.floors,
    struct_columns: interface.struct_columns,
    beams: interface.beams,
    ceilings: interface.ceilings,
    columns: interface.columns
}

selected_category_A = forms.CommandSwitchWindow.show(
    [key for key in category_names_and_elements], 
    message="Selecione uma categoria (1/2):"
)

selected_category_B = forms.CommandSwitchWindow.show(
    [key for key in category_names_and_elements],
    message="Selecione uma categoria (2/2):"
)

def perform_batch_join(doc, elements_A, elements_B):
    for elem_A in elements_A:
            elem_A_geometry = elem_A.get_Geometry(DB.Options())

            for elem_A_geometry_object in elem_A_geometry:
                if isinstance(elem_A_geometry_object, DB.Solid) and elem_A_geometry_object.Volume > 0:
                    for elem_B in elements_B:
                        elem_B_geometry = elem_B.get_Geometry(DB.Options())
                        
                        for elem_B_geometry_object in elem_B_geometry:
                            if isinstance(elem_B_geometry_object, DB.Solid) and elem_B_geometry_object.Volume > 0:
                                intersection = DB.BooleanOperationsUtils.ExecuteBooleanOperation(
                                    elem_A_geometry_object, 
                                    elem_B_geometry_object, 
                                    DB.BooleanOperationsType.Intersect
                                    )
                                if intersection and intersection.Volume > 0:
                                    DB.JoinGeometryUtils.JoinGeometry(doc, elem_A, elem_B)
                                

def join_geometry(doc, category_A, category_B):
    elements_A = category_names_and_elements[category_A]
    elements_B = category_names_and_elements[category_B]

    t = DB.Transaction(doc, "Join cutting solids")
    t.Start()

    try:
        perform_batch_join(doc, elements_A, elements_B)
    except Exception as e:
        print("Erro: {}".format(e))
    finally:
        t.Commit()

join_geometry(doc, selected_category_A, selected_category_B)