# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from revit_doc_interface import (RevitDocInterface)
from pyrevit import forms

interface = RevitDocInterface()

__title__     = "Batch Join Geometry"
doc = __revit__.ActiveUIDocument.Document

category_names_and_elems = {
    "Walls": interface.walls,
    "Floors": interface.floors,
    "Ceilings": interface.ceilings,
    "Structural Columns": interface.struct_columns,
    "Columns": interface.columns,
    "Beams": interface.beams
}

level = forms.CommandSwitchWindow.show(
    [level for level in interface.levels], 
)

category_A = forms.CommandSwitchWindow.show(
    [key for key in category_names_and_elems]
    # message="Selecione a segunda categoria para unir os elemos"
)

category_B = forms.CommandSwitchWindow.show(
    [key for key in category_names_and_elems if key != category_A]
    # message="Selecione a segunda categoria para unir os elemos"
)

def get_elem_geometry(elem):
    return elem.get_Geometry(DB.Options())

def validate_geometry_as_solid(elem_geometry_unit):
    return isinstance(elem_geometry_unit, DB.Solid) and elem_geometry_unit.Volume > 0
        
def elements_overlap(elem_A_geometry_unit, elem_B_geometry_unit):
    intersection = DB.BooleanOperationsUtils.ExecuteBooleanOperation(
        elem_A_geometry_unit, 
        elem_B_geometry_unit,
        DB.BooleanOperationsType.Intersect
    )
    return intersection and intersection.Volume > 0
        
def join_geometry(doc, category_A, category_B):
    elems_A = category_names_and_elems[category_A]
    elems_B = category_names_and_elems[category_B]

    try:
        for elem in elems_A:
            elem_geometry = elem.get_Geometry(DB.Options())

            for elem_A_geometry_unit in elem_geometry:
                if validate_geometry_as_solid(elem_A_geometry_unit):
                    for elem_B in elems_B:
                        elem_B_geometry = elem_B.get_Geometry(DB.Options())
                        
                        for elem_B_geometry_unit in elem_B_geometry:
                            if isinstance(elem_B_geometry_unit, DB.Solid) and elem_B_geometry_unit.Volume > 0:      
                                if elements_overlap(elem_A_geometry_unit, elem_B_geometry_unit):
                                    t = DB.Transaction(doc, "Join overlapping geometries")
                                    t.Start()

                                    try:
                                        
                                        DB.JoinGeometryUtils.JoinGeometry(doc, elem, elem_B)
                                        print("elemos unidos: {} (ID {}) + {} (ID {})".format(elem.Name, elem.Id, elem_B.Name, elem_B.Id))
                                    
                                    except Exception as e:
                                        print("Erro ao unir geometria: {}".format(e))
                                    finally:
                                        t.Commit()
    except Exception as e:
        print("Erro geral na transação: {}".format(e))


join_geometry(doc, category_A, category_B)