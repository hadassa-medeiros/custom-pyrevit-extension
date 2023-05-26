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
room_id = revit.ElementId(1123259)  # Replace 123 with the actual ElementId
# Get the room element from the ElementId
room = doc.GetElement(room_id)

parameter_set = room.Parameters
print(parameter_set)



# room_name_param = parameter_set[revit.BuiltInParameter.ROOM_NAME]
# print(room_name_param)