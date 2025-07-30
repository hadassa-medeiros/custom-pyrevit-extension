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

def can_be_joined(elem_geometry_unit_A, elem_geometry_unit_B):
    def is_solid(geometry_unit):
        return isinstance(geometry_unit, DB.Solid) and geometry_unit.Volume > 0
  
    def elements_overlap(e1, e2):
        intersection = DB.BooleanOperationsUtils.ExecuteBooleanOperation(
            e1, 
            e2,
            DB.BooleanOperationsType.Intersect
        )
        return intersection and intersection.Volume > 0
    
    can_be_joined = is_solid(elem_geometry_unit_A) and is_solid(elem_geometry_unit_B) and elements_overlap(elem_geometry_unit_A, elem_geometry_unit_B)
    
    return can_be_joined

def join_geometries(el1, el2):
    with DB.Transaction(doc, "Join overlapping geometries") as t:
        t.Start()
        try:
            DB.JoinGeometryUtils.JoinGeometry(doc, el1, el2)
        except Exception as e:
            print("Error joining geometries: {}".format(e))
            pass
        t.Commit()

category_A = forms.CommandSwitchWindow.show(
    [key for key in category_names_and_elems]
)

category_B = forms.CommandSwitchWindow.show(
    [key for key in category_names_and_elems if key != category_A]
)

elems_A = category_names_and_elems[category_A]
elems_B = category_names_and_elems[category_B]
        
for elem_A in elems_A:
    for elem_B in elems_B:
        if can_be_joined(elem_A, elem_B):
            join_geometries(elem_A, elem_B)