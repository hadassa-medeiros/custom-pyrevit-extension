# -*- coding: utf-8 -*-
import clr

clr.AddReference('RevitAPI')
import Autodesk.Revit.DB as DB
import Autodesk.Revit.UI.Selection as sel
import Autodesk.Revit.UI as UI
import Autodesk.Revit.DB.Events as events
from pyrevit import forms

__title__     = "room separator from curtain wall"
__author__    = "Hadassa Medeiros"
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# doc = uidoc.Document
app = __revit__.Application
double_to_meter_divisor = 3.28084

walls_collector = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls)
wall_curtains_collector = list(walls_collector.WhereElementIsNotElementType().ToElements())

# levels = list(levels_collector.WhereElementIsNotElementType().ToElements())
# room_separation_lines = 

for wall in walls_collector:
        if wall.CurtainGrid is not None or wall.WallType.Kind == "curtain":
                # wall_type = wall.
                print(wall.WallType.FamilyName)
                t = DB.Transaction(doc, "Create room separator based on curtain walls' coordinates")
                t.Start()
                
                t.Commit()

# for selected_ in selected_r:
#     selected_room_element = next(room for room in rooms if
#                                  room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString() == selected_room_number)
#     room = doc.GetElement(selected_room_element.Id)

#     room_id = room.Id.ToString()
#     room_elem = doc.GetElement(DB.ElementId(int(room_id)))
#     print(type(room_area))

#     room_bbox = room.get_BoundingBox(doc.ActiveView)
#     room_outline = DB.Outline(room_bbox.Min, room_bbox.Max)
#     # Establishing rooms as filters to elements

#     for level in levels:
#         try:
#             level_above = levels[levels.index(level) + 1]
#             level_above_elev = level_above.get_Parameter(DB.BuiltInParameter.LEVEL_ELEV).AsDouble()
#             floor_to_floor_height = level_above_elev - room_level_elev # This value is in the Revit's format AsDouble, not in meters.
#             if room.Level.Id == level.Id and floor_to_floor_height > 0:
#                 print('ok')
#                 t = DB.Transaction(doc, "Change room's upper offset value in meters")
#                 t.Start()
#                 room_upper_offset.Set(floor_to_floor_height - .7)
#                 t.Commit()
#                 print("Upper offset parameter value of the room {} has been modified to {}m.".format(room_name, ((floor_to_floor_height - .7)/double_to_meter_divisor)))
#             elif floor_to_floor_height == 0:
#                 t = DB.Transaction(doc, "Do nothing, leave it be")
#                 t.Start()
#                 room_upper_offset.Set(room_default_height_offset)
#                 t.Commit()
#         except IndexError:
#             pass