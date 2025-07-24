# -*- coding: utf-8 -*-
import clr
from revit_doc_interface import (get_name)


clr.AddReference('RevitAPI')
import Autodesk.Revit.DB as DB
import Autodesk.Revit.UI.Selection as sel
from pyrevit import forms

__title__     = "Adjust Room Base Offset"
__author__    = "Hadassa Medeiros"
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument


# doc = uidoc.Document
app = __revit__.Application

levels_collector =    DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Levels)
rooms_collector = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms)

rooms = list(rooms_collector.WhereElementIsNotElementType().ToElements())
levels = list(levels_collector.WhereElementIsNotElementType().ToElements())

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

    room_lower_offset = room.get_Parameter(DB.BuiltInParameter.ROOM_LOWER_OFFSET)
    room_levels_computation_height = (room.Level).get_Parameter(DB.BuiltInParameter.LEVEL_ROOM_COMPUTATION_HEIGHT)
    room_name = room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
    if room_levels_computation_height.AsValueString() != room_lower_offset.AsValueString():
        try:
            t = DB.Transaction(doc, "Change room's lower offset value")
            t.Start()
            room_lower_offset.Set(room_levels_computation_height.AsDouble())
            t.Commit()
            print("Lower offset value for room {} - {} successfully set to {} m."
                    .format(
                        room.Number,
                        get_name(room), 
                        room_levels_computation_height.AsValueString()
                        )
                )
        except Exception as e:
            print("An error occurred: {}".format(e))
            if t.HasStarted() and not t.HasEnded():
                t.RollBack()