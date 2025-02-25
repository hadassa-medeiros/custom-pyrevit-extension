# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from revit_doc_interface import (RevitDocInterface, get_name)
from pyrevit import forms


interface = RevitDocInterface()

__title__     = "Unir geometrias intersectantes"
__author__    = "Hadassa Medeiros"
doc = __revit__.ActiveUIDocument.Document

# listar categorias cujos elementos sejam solidos (passiveis de ter suas geometrias unidas com outras)
# filtro?

# def find_out_categories_with_solids():
#     categories_with_solids = []
#     for elem in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements():
#         if elem.get_Geometry(DB.Options()) is not None:
#             print(elem)
#             # categories_with_solids.append(cat)
#     print(categories_with_solids)

# find_out_categories_with_solids()


# pedir para que o usuario selecione categorias cujos elementos intersectantes devem ser unidos
category_names_and_elements = {
    DB.BuiltInCategory.OST_Walls: interface.walls,
    DB.BuiltInCategory.OST_Floors: interface.floors,
    DB.BuiltInCategory.OST_StructuralColumns: interface.struct_columns,
    DB.BuiltInCategory.OST_StructuralFraming: interface.beams,
    DB.BuiltInCategory.OST_Ceilings: interface.ceilings,
    DB.BuiltInCategory.OST_Columns: interface.columns
}

# # passar as categorias para funcao que ira lidar com a transaction

selected_category_A = forms.CommandSwitchWindow.show(
    [key for key in category_names_and_elements], 
    message="Selecione um nível para verificar os elementos associados"
)

selected_category_B = forms.CommandSwitchWindow.show(
    [key for key in category_names_and_elements],
    message="Selecione uma categoria de elementos para verificar os associados ao piso selecionado"
)

def join_geometry(doc, category_A, category_B):
    elements_A = category_names_and_elements[category_A]
    elements_B = category_names_and_elements[category_B]

    t = DB.Transaction(doc, "Join cutting solids")
    t.Start()

    try:
        for elem_A in elements_A:
            # Obtém a geometria do elemento
            elem_A_geometry = elem_A.get_Geometry(DB.Options())
            # print(elem_A.Id, elem_A.Name)

            # Itera sobre todos os objetos geométricos do elemento
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
                                    try:
                                        DB.JoinGeometryUtils.JoinGeometry(doc, elem_A, elem_B)
                                        print("Elementos unidos: {} (ID {}) + {} (ID {})".format(elem_A.Name, elem_A.Id, elem_B.Name, elem_B.Id))
                                    except Exception as e:
                                        print("Erro ao unir geometria: {}".format(e))
    except Exception as e:
        print("Erro geral na transação: {}".format(e))
    finally:
        # Comita a transação ao final
        t.Commit()

# chama a funcao para performar o batch join
join_geometry(doc, selected_category_A, selected_category_B)