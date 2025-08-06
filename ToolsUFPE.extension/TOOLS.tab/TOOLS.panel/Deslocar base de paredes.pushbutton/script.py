from _base import * # pyright: ignore[reportMissingImports]
import _snippets as sn # pyright: ignore[reportMissingImports]
import csv
import Autodesk.Revit.DB as db

__title__  = "Change wall base offset"
__author__ = "hadassa.lima@ufpe.br"


c = sn.ElementCollections()

new_offset_m = -.04
new_offset = new_offset_m * 3.28084 

""" for wall in c.walls:
    name = sn.get_type_name(wall)
    param = db.BuiltInParameter.WALL_BASE_OFFSET
    elem_param = wall.get_Parameter(param)
    param_name = elem_param.AsValueString()

    if "GENERICA" in name:
        print(name)
        sn.set_value(wall, param, new_offset, __title__) """
name = sn.get_type_name(c.walls[0])
param = db.BuiltInParameter.WALL_BASE_OFFSET
elem_param = c.walls[0].get_Parameter(param)
param_name = elem_param.AsValueString()

if "GENERICA" in name:
    print(name)
    sn.set_value(c.walls[0], param, new_offset, __title__)