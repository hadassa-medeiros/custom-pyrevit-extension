# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from revit_doc_interface import (RevitDocInterface, GetCeilingHeight, ModelLine, find_id_by_element_name, get_name, get_names, metric_to_double, double_to_metric)

__title__     = "Desativar delimitação de ambientes para divisórias"
__annotations__ = "Desligar delimitacao de ambientes para todas as parede tipo DIV_ em WCs"
__author__    = "Hadassa Medeiros"

doc = __revit__.ActiveUIDocument.Document
interface = RevitDocInterface()

all_rooms = interface.rooms
all_walls = interface.walls

for wall in all_walls:
    name = get_name(wall)
    wall_width = double_to_metric(wall.Width)
    level_id = wall.LevelId
    
    # Tenta acessar o parâmetro WALL_ATTR_ROOM_BOUNDING
    room_bounding_param = wall.get_Parameter(DB.BuiltInParameter.WALL_ATTR_ROOM_BOUNDING)
    
    # Condições de modificação do parâmetro
    if room_bounding_param and 'DIV' in name and wall_width <= 0.04 and room_bounding_param.AsInteger() == 1:        
        try:
            print("Desativando Delimitação de ambientes para a parede: {}".format(name))

            # Inicia uma transação para alterar o parâmetro
            t = DB.Transaction(doc, "Switch off room bounding for wall")
            t.Start()
            print(
                "Room Bounding (Before) for Wall ID {}: {}"
                .format(wall.Id.IntegerValue, room_bounding_param.AsInteger())
                )
            room_bounding_param.Set(0)  # Define como 0 (false)
            print(
                "Room Bounding (After) for Wall ID {}: {}"
                .format(wall.Id.IntegerValue, room_bounding_param.AsInteger())
                )
            t.Commit()

        except Exception as e:
            print("Erro ao desativar Delimitação de ambientes para a parede {}: {}".format(name, e))
            pass
        
    else:
        print("A divisória ID {} já apresenta Delimitação de ambientes desativada.".format(wall.Id))
            