from pyrevit import forms, revit, DB, UI
import Autodesk.Revit.DB as revit

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application