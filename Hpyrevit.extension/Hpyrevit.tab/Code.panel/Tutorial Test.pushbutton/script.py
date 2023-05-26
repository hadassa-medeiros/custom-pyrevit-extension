from pyrevit import forms, revit, DB, UI
import Autodesk.Revit.DB as revit

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

e_id        = revit.ElementId(1123259)

element = doc.GetElement(e_id)

#GET INFO
# e_cat       = element.Category

# e_level_id  = element.LevelId
# e_wall_type = element.WallType
# e_width     = element.Width

print(e_id)

print(element)

#trying to acces the parameter room_name of some random room:
room1_id = revit.ElementId(1123259)  # Replace 123 with the actual ElementId
room2_id = revit.ElementId(347079)
# Get the room element from the ElementId
room1 = doc.GetElement(room1_id)
room2 = doc.GetElement(room2_id)
param_set1 = room1.Parameters.Size


#now, testing how to get information from multiple elements inside the project(proper loops and methods to be used
# as nexts steps):
list_of_rooms = [room1, room2]
for room in list_of_rooms:
    param_set = room.Parameters.Size
    print('{} has {} parameters inside it.'.format(room,param_set))


# room_name_param = parameter_set[revit.BuiltInParameter.ROOM_NAME]
# print(room_name_param)