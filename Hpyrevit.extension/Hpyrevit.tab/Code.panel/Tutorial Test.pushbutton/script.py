# from Autodesk.Revit.DB import *
# it is the incorrect approach to load it ONCE YOU'RE USING IRONPYTHON (hence the error
# OSError: IronPython.Runtime.Exceptions.OSException: cannot load library C:\Program Files\Autodesk\Revit 2023):
# import ctypes
# revit_api = ctypes.CDLL("C:\Program Files\Autodesk\Revit 2023\RevitAPI.dll")

# import clr
# clr.AddReferenceToFileAndPath("C:\Program Files\Autodesk\Revit 2023\RevitAPI")
# clr.AddReference("RevitAPI")

# from rpw import revit, db
# from rpw.ui.forms import (FlexForm, Label, ComboBox, TextBox, TextBox,Separator, Button, CheckBox)
# from rpw.ui.forms import select_file

from pyrevit import forms, revit, DB, UI
import Autodesk.Revit.DB as revit

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

e_id        = revit.ElementId(628523)

element = doc.GetElement(e_id)

#GET INFO
# e_cat       = element.Category

# e_level_id  = element.LevelId
# e_wall_type = element.WallType
# e_width     = element.Width

print(e_id)
print(element)

# from rpw.db.xyz import XYZ
#
# doc = Revit.UI.UIApplication.ActiveUIDocument
# doc = revit.ActiveUIDocument.Document
#
# def create_elements_on_floors(element_type, parameters):
#
#     transaction = Revit.DB.Transaction(doc, "Batch Element Creation")
#     transaction.Start()
#
#     # for level in levels:
#     #     level_name = level.Name
#
#         # Create element on each floor
#     element = doc.Create.NewFamilyInstance(XYZ(0, 0, 0), element_type, structural_type)
#
#         # Set element parameters
#     for param_name, param_value in parameters.items():
#         parameter = element.LookupParameter(param_name)
#         if parameter is not None:
#             parameter.Set(param_value)
#
#
#         # Modify other element properties or perform additional actions
#
#     transaction.Commit()
#
# # Example usage
# element_type = Revit.DB.ElementId(398)  # Replace with the actual element type ID
# # levels = [doc.GetElement(ElementId(311)), doc.GetElement(ElementId(694))]  # Replace with the actual level IDs
# structural_type = Revit.DB.Structure.StructuralType.NonStructural
# parameters = {
#     "Height": 3.0,
#     "Width": 2.5,
#     "Material": "Concrete"
# }
#
#
# create_elements_on_floors(element_type, parameters)
#





# import clr
# from pyrevit import framework
# from pyrevit import revit, DB, UI, forms
#
#
# # Import RevitAPI
# clr.AddReference("RevitAPI")
# from Autodesk.Revit.DB import *
#
# doc = __revit__.ActiveUIDocument.Document
# uidoc = __revit__.ActiveUIDocument
# app = __revit__.Application
#
# elem = ElementId()
# print(elem)
# e_cat       = element.Category
# e_id        = element.Id
# e_level_id  = element.LevelId
# e_wall_type = element.WallType
# e_width     = element.Width






# ----------
# from pyrevit import forms, revit, DB, UI
# import Autodesk.Revit as revit
#
# doc = __revit__.ActiveUIDocument.Document
# uidoc = __revit__.ActiveUIDocument
# app = __revit__.Application
#
# with forms.WarningBar(title='Pick an element:'):
#     element = revit.pick_element()
#
# print(element)
#
# #GET INFO
# e_cat       = element.Category
# e_id        = element.Id
# e_level_id  = element.LevelId
# e_wall_type = element.WallType
# e_width     = element.Width