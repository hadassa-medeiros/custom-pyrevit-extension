# -*- coding: utf-8 -*-
import clr

clr.AddReference('RevitAPI')
import Autodesk.Revit.DB as DB
import Autodesk.Revit.UI.Selection as sel
from pyrevit import forms
# from rpw import revit, db, ui, forms

__title__     = "rooms' upper offset"
__author__    = "Hadassa Medeiros"
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument


# doc = uidoc.Document
app = __revit__.Application

levels_collector =    DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Levels)
rooms_collector = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms)

rooms = list(rooms_collector.WhereElementIsNotElementType().ToElements())
levels = list(levels_collector.WhereElementIsNotElementType().ToElements())

double_to_meter_divisor = 3.28084

rooms_total = 0 #Quantity of rooms analyzed.
room_numbers_and_names = ["{} - {}".format(
    room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString(),
    room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
) for room in rooms]

# Show a checkbox list for room selection

selected_rooms_and_names = forms.SelectFromList.show(room_numbers_and_names, button_name='Select Rooms', multiselect=True)

# Iterate through selected room numbers (they are unique, unlike room names that can be repeated within the same model) and get the corresponding room elements
selected_room_numbers = [selected.split(" - ")[0] for selected in selected_rooms_and_names] #refers only to the relement's name, for each element selected.
selected_room_names = [selected.split(" - ")[1] for selected in selected_rooms_and_names]

for selected_room_number in selected_room_numbers:
    selected_room_element = next(room for room in rooms if
                                 room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString() == selected_room_number)
    room = doc.GetElement(selected_room_element.Id)
    print('{}------------------------------'.format(room.Number))

    # Useful information about project's rooms:
    room_default_height_offset = int(3 * 3.28084)  # Value AsDouble that Equals to 2.74m
    room_upper_offset = room.get_Parameter(DB.BuiltInParameter.ROOM_UPPER_OFFSET)
    room_level_elev = (room.Level).get_Parameter(DB.BuiltInParameter.LEVEL_ELEV).AsDouble()
    room_upper_level = room.get_Parameter(DB.BuiltInParameter.ROOM_UPPER_LEVEL).AsElementId()
    room_id = room.Id.ToString()
    room_name = room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
    room_elem = doc.GetElement(DB.ElementId(int(room_id)))
    room_area = float((room.get_Parameter(DB.BuiltInParameter.ROOM_AREA).AsValueString())[:4])
    print(type(room_area))

    room_bbox = room.get_BoundingBox(doc.ActiveView)
    room_outline = DB.Outline(room_bbox.Min, room_bbox.Max)
    # Establishing rooms as filters to elements
    room_as_filter = DB.BoundingBoxIntersectsFilter(room_outline)# Create filter
    intersecting_elem = DB.FilteredElementCollector(doc).WherePasses(room_as_filter).ToElements() # Using filter to retrieve elements
    # list_python_collected_elements = ['room {}: {}'.format(room),list(collected_intersecting_elements)]


    for level in levels:
        try:
            level_above = levels[levels.index(level) + 1]
            level_above_elev = level_above.get_Parameter(DB.BuiltInParameter.LEVEL_ELEV).AsDouble()
            floor_to_floor_height = level_above_elev - room_level_elev # This value is in the Revit's format AsDouble, not in meters.
            if room.Level.Id == level.Id and floor_to_floor_height > 0:
                print('ok')
                t = DB.Transaction(doc, "Change room's upper offset value in meters")
                t.Start()
                room_upper_offset.Set(floor_to_floor_height - .7)
                t.Commit()
                print("Upper offset parameter value of the room {} has been modified to {}m.".format(room_name, ((floor_to_floor_height - .7)/double_to_meter_divisor)))
            elif floor_to_floor_height == 0:
                t = DB.Transaction(doc, "Do nothing, leave it be")
                t.Start()
                room_upper_offset.Set(room_default_height_offset)
                t.Commit()
        except IndexError:
            pass
    print('fim')