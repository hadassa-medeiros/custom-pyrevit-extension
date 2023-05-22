from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, BuiltInParameter

doc = __revit__.ActiveUIDocument.Document

wall_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType()

total_area = 0.0
print(wall_collector)

for wall in wall_collector:
    area_param = wall.Parameter[BuiltInParameter.HOST_AREA_COMPUTED]
    if area_param:
        total_area = total_area + area_param.AsDouble()
print("Total area of walls is {:.2f}".format(total_area))


