from Autodesk.Revit.DB import *

from pyrevit import revit

doc = revit.ActiveUIDocument.Document
uidoc = revit.ActiveUIDocument
app = revit.Application

element_type = type(element)
print(element_type)

all_doors = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls)

print(all_doors)
