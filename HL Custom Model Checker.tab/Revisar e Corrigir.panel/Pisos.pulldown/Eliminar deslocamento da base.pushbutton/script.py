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
__doc__       = "Elimina o deslocamento da base de todos os pisos do projeto cujo valor de deslocamento seja diferente do padrao (0.00)"

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
            #   # if there is no level with the sufix -ossatura, create one below the current level by 2cm

                # else:
                #     t = DB.Transaction(doc, "Criar nível de topo da parede")
                #     t.Start()
                #     try:
                #         level = DB.Level.Create(doc, constraint_level.Elevation - 0.02)
                #         level.Name = constraint_level.Name + '-ossatura'
                #         wall.get_Parameter(DB.BuiltInParameter.WALL_HEIGHT_TYPE).Set(level.Id)
                #         print("Nível de topo da parede {} - {} corrigido de {} para nivel recem-criado {}".format(wall.Name, wall.Id, constraint_level.Name, level.Name))
                #     except Exception as e:
                #         print("Error: {}".format(e))
                #         pass
                    
correct_wall_top_constraint()

'''
walls are used in layering systems, where each layer has a specific function and material
one core wall element represents the core/nucleus of the wall, plus the substract or pre-finishing layers

walltype names must be
    composed by 3 parts: prefix["REV_", ALV_, "" + "wall name" + "wall.width in cm", all upper case except for the wall name(capitalized, no special characters)
REV_s:
    1. have their compound strucutre composed by only one layer
    2. this layer must have its function (layer.Function) set to "Finish2"
    3. this layer must not have its material (layer.Material) empty (None or <By Category> or <Por Categoria>)

    if wall name prefix is anything other than standard
    correct it to the standard based on the unique characteristics of the walltype
GENERICA_xCM
ALV_s:
    1. have their core layer with function "Structure"
    2. have their core layer with structural materials, such as "Concrete" or "Masonry" (concreto ou alvenaria)
    3. have their compound structure's total thickness (equivalent to wall.Width) of x cm (need conversion from double to m to cm)
    4. have their surface (most externcal and most internal) layers 
        with function "Substrate" or "Finish1", but never "Finish2" or "Structure"
    
    '''