# -*- coding: utf-8 -*-
from revit_doc_interface import (RevitDocInterface, get_name)
import operator
import csv
from pyrevit import forms
from custom_forms import CustomInput
import Autodesk.Revit.DB as DB
doc = __revit__.ActiveUIDocument.Document

__title__     = "Eliminar deslocamento da base"
__author__    = "Hadassa Medeiros"
__doc__       = ""

interface = RevitDocInterface()

def remove_base_offset():
    for floor in interface.floors:
        height_above_level = floor.get_Parameter(DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).AsDouble()
        if height_above_level != 0:
            t = DB.Transaction(doc, "Eliminar deslocamento da base")
            t.Start()
            try:
                floor.get_Parameter(DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).Set(0)
                print("Deslocamento da base do piso {} - {} eliminado".format(floor.Name, floor.Id))
            except Exception as e:
                print("Error: {}".format(e))
                pass
            t.Commit()  

def correct_wall_top_constraint():
    for wall in interface.walls:
        top_constraint = wall.get_Parameter(DB.BuiltInParameter.WALL_HEIGHT_TYPE).AsElementId()
        if str(top_constraint) != '-1':
            constraint_level = doc.GetElement(top_constraint)
            # print(constraint_level.Name)
            if 'Ossatura'.lower not in constraint_level.Name.lower():
                # print(constraint_level.Name)
                # set it to the respective level (terreo, 1o pavimento etc), but with the sufix -ossatura
                # find in the interface.levels the one whose name matcher constraint_level.Name + '-ossatura'
                level = next((level for level in interface.levels if level.Name.lower() == constraint_level.Name.lower() + '-ossatura'), None)
                if level: 
                    # print(level.Name)          
                    t = DB.Transaction(doc, "Corrigir nível de topo da parede")
                    t.Start()
                    try:
                        wall.get_Parameter(DB.BuiltInParameter.WALL_HEIGHT_TYPE).Set(level.Id)
                        print("Nível de topo da parede {} - {} corrigido de {} para {}".format(wall.Name, wall.Id, constraint_level.Name, level.Name))
                    except Exception as e:
                        print("Error: {}".format(e))
                        pass
                    t.Commit()
correct_wall_top_constraint()

