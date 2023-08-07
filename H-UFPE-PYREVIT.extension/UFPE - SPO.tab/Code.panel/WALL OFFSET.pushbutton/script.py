# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB

doc = __revit__.ActiveUIDocument.Document
app = __revit__.Application

levels = list(DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Levels).
              WhereElementIsNotElementType().ToElements())

rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

ceilings_category = str(DB.BuiltInCategory.OST_Ceilings)
walls_category = str(DB.BuiltInCategory.OST_Walls)
floors_category = str(DB.BuiltInCategory.OST_Floors)

double_to_meter_divisor = 3.28084

# ITERATING THROUGH EVERY LEVEL FROM LOWEST TO HIGHEST:
for room in rooms:
    try:
        room_name = room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
        room_default_height_offset = int(3 * 3.28084) # Value AsDouble that Equals to 2.74m
        room_upper_offset = room.get_Parameter(DB.BuiltInParameter.ROOM_UPPER_OFFSET)
        room_level_elev = (room.Level).get_Parameter(DB.BuiltInParameter.LEVEL_ELEV).AsDouble()
        room_upper_level = room.get_Parameter(DB.BuiltInParameter.ROOM_UPPER_LEVEL).AsElementId()
    except AttributeError:
        pass
# Establishing rooms as filters to elements
    for level in levels:
        try:
            level_above = levels[levels.index(level) + 1]
            level_above_elev = level_above.get_Parameter(DB.BuiltInParameter.LEVEL_ELEV).AsDouble()
            floor_to_floor_height = level_above_elev - room_level_elev # This value is in the Revit's format AsDouble, not in meters.

            if room.Level.Id == level.Id and floor_to_floor_height > 0:
                # print(room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString())
                t = DB.Transaction(doc, "Changing room's upper offset")
                t.Start()
                room_upper_offset.Set(floor_to_floor_height - .7)
                t.Commit()
                # print(
                #     "Upper offset parameter value of the room {} has been successfully modified to {}m.".format(
                #     room_name, (floor_to_floor_height/double_to_meter_divisor)
                #         ))
            elif floor_to_floor_height == 0:
                t = DB.Transaction(doc, "Changing room's upper offset")
                t.Start()
                room_upper_offset.Set(room_default_height_offset)
                t.Commit()
        except IndexError:
            break
