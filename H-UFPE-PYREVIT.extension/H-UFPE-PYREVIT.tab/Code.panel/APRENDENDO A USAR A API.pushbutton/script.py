# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as revit

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

# tutorial parameteres:https://www.youtube.com/watch?v=YoLxucuC6Ss
wall_id = doc.GetElement(revit.ElementId(335641))
print(list(wall_id.Parameters))

for p in wall_id.Parameters:
    print('\n{}'.format(p.Definition.Name))
    print(p.Definition.BuiltInParameter)
    print(p.IsReadOnly)
    print(p.StorageType)


# area_tags = revit.FilteredElementCollector(doc).OfCategory(revit.BuiltInCategory.OST_AreaTags).ToElements()
# print(area_tags)
#
# all_furniture = revit.FilteredElementCollector(doc)
# all_furniture.OfCategory(revit.BuiltInCategory.OST_Furniture)
# all_furniture.WhereElementIsNotElementType()
# all_furniture.ToElements()
# print(all_furniture)
#
# type_name = doc.get_Parameter(revit.BuiltInParameter.OST_AreaTags).AsDouble()
# print(type_name)






# from pyrevit import DB, UI
# from pyrevit import forms
#
# forms.ask_for_string(
#     default='some-tag',
#     prompt='Enter new tag name:',
#     title='Tag'
# )
# forms.
# DB.