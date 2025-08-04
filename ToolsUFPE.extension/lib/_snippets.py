# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB 
from _base import *


def get_selected():
    return [doc.GetElement(elem_id) for elem_id in uidoc.Selection.GetElementIds()]

def get_name(elem):
    if elem is not None:
        model_type_param = elem.get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_NAME)
        room_name_param = elem.get_Parameter(DB.BuiltInParameter.ROOM_NAME)
        
        model_type_name = model_type_param.AsString() if model_type_param else None
        room_name = room_name_param.AsString() if room_name_param else None

        # Prioriza o nome do tipo de modelo
        if room_name is not None:
            name = room_name
        elif elem.Name:
            name = elem.Name
        elif model_type_name is not None:
            name = model_type_name
        else:
            name = "S/N"
        
        return name
        # return capitalize_string(remove_acentos(name))

    return "elemo inválido"