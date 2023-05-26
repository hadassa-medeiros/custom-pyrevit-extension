from pyrevit import forms, revit, DB, UI
import Autodesk.Revit.DB as revit

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

e_id        = revit.ElementId(2219611)

element = doc.GetElement(e_id)

#GET INFO
# e_cat       = element.Category
# e_level_id  = element.LevelId
# e_wall_type = element.WallType
# e_width     = element.Width

print(e_id)

print(element)

#trying to acces the parameter room_name of some random room:
room1_id = revit.ElementId(1123259)  #Ambiente WC M. - 1 PAVTO
room2_id = revit.ElementId(611306) #Ambiente HALL - 1 PAVTO
# Get the room element from the ElementId
# room1 = doc.GetElement(room1_id)
# room2 = doc.GetElement(room2_id)

#now, testing how to get information from multiple elements inside the project(proper loops and methods to be used
# as nexts steps):
list_of_rooms_by_id = [room1_id, room2_id]
for id in list_of_rooms_by_id:
    room = doc.GetElement(id)
    param_set = room.Parameters.Size
    print('{} has {} parameters inside it.'.format(room,param_set))
    print(room.Area/10.764)
    print(room.CanBeHidden) # with this synthax being used, it doesn't return TRUE or FALSE despite being boolean.
    #what then woul di write to retrieve a True for the CanBeHidden method? https://www.revitapidocs.com/2015/887010c4-de58-96b6-0931-4c226e6b142b.htm
    print(room.Level.Name)


# room_name_param = parameter_set[revit.BuiltInParameter.ROOM_NAME]
# print(room_name_param)