# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from revit_doc_interface import (RevitDocInterface, get_name, double_to_metric)

__title__     = "Desativar delimitação de ambientes para divisórias"
__annotations__ = "Desligar delimitacao de ambientes para todas as parede tipo DIV_ em WCs"
__author__    = "Hadassa Medeiros"

doc = __revit__.ActiveUIDocument.Document
interface = RevitDocInterface()

all_rooms = interface.rooms
all_walls = interface.walls
wcs = [
    room for room in all_rooms 
    if any(
        keyword.lower() in get_name(room).strip().lower() for keyword in ['wc']
        )
    ]

# Percorrer apenas os ambientes WC/WCB/Sanitarios
for room in wcs:
    print(room.Id, get_name(room))
    room_bbox = room.get_BoundingBox(doc.ActiveView)
    room_as_filter = DB.BoundingBoxIntersectsFilter(DB.Outline(room_bbox.Min, room_bbox.Max)) # Create filter
    # collect only walls within wcs bounding boxes
    walls_inside_room = DB.FilteredElementCollector(doc).OfCategory(
        DB.BuiltInCategory.OST_Walls
        ).WherePasses(room_as_filter).ToElements()

    print("WIP: Desativando delimitação de ambientes para divisórias em WCs")

    for wall in walls_inside_room:
        name = wall.Name
        wall_width = double_to_metric(wall.Width)
        wall_height = double_to_metric(wall.get_Parameter(DB.BuiltInParameter.WALL_USER_HEIGHT_PARAM).AsDouble())
        # level_id = wall.LevelId
        room_bounding_param = wall.get_Parameter(DB.BuiltInParameter.WALL_ATTR_ROOM_BOUNDING)
        
        # Apenas se o nome da parede contiver o termo DIV (indica que se trata de divisoria) e o parâmetro Delimitação de ambientes estiver ativo, desativa-lo
        if 'DIV'.lower() == name.split("_")[0].lower() and room_bounding_param.AsInteger() == 1:        
            try:
                print("Desativando Delimitação de ambientes para a parede: {} - ID {}".format(name, wall.Id))

                # Inicia uma transação para alterar o parâmetro
                t = DB.Transaction(doc, "Switch off room bounding for wall")
                t.Start()
                room_bounding_param.Set(0)  # Define como 0 (false) o parâmetro Delimitação de ambientes    
                t.Commit()

            except Exception as e:
                print("Erro ao desativar Delimitação de ambientes para a parede {}: {}".format(name, e))
                pass
            
        else:
            print("{} - ID {} já apresenta divisorias internas com Delimitação de ambientes desativada.".format(get_name(room),(room.Id)))