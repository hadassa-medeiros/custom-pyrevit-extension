# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

# Object references
walls_collector =   DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls)
wall_instances = walls_collector.WhereElementIsNotElementType().ToElements()
walls_collector =   DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls)
phases = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Phases)

for wall in wall_instances:

    # Retrieving phase of creation through a built in parameter
    wall_phase_created = wall.get_Parameter(DB.BuiltInParameter.PHASE_CREATED)
    created_str = wall_phase_created.AsValueString()
    wall_phase_demolished = wall.get_Parameter(DB.BuiltInParameter.PHASE_DEMOLISHED)
    demolished_str = wall_phase_demolished.AsValueString()

    # Shared parameters that will act as filters to infill type of walls (yes/no)
    wall_to_build = wall.LookupParameter('CONSTRUIR-FASE')
    wall_to_demolish = wall.LookupParameter('DEMOLIR-FASE')

    # Filtering the elements and attributing the paramaters to the shared parameters check boxes

    if created_str == 'Projeto':
        t = DB.Transaction(doc, "assigning value to element's parameter")
        t.Start()
        wall_to_build.Set(created_str)
        t.Commit()

    elif wall_phase_demolished.AsValueString() == 'Projeto':
        t = DB.Transaction(doc, "assigning value to element's parameter")
        t.Start()
        wall_to_demolish.Set(demolished_str)
        t.Commit()


# ALTERNATIVE to either act as a double check or as a stand alone way to filter infill walls, which do not support profile sketch as "standard" wall elements do.
if wall.CanHaveProfileSketch == False:
    print('this wall is not being included')
    # ...
