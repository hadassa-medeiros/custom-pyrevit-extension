# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

walls_collector =   DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls)
wall_instances = walls_collector.WhereElementIsNotElementType().ToElements()
walls_collector =   DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls)
phases = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Phases)

for wall in wall_instances:
    # Retrieving phase of creation through an element's property
    # wall_phase_created = doc.GetElement(DB.ElementId(int(wall.CreatedPhaseId.ToString())))

    # Retrieving phase of creation through a built in parameter
    wall_phase_created = wall.get_Parameter(DB.BuiltInParameter.PHASE_CREATED)
    wall_phase_demolished = wall.get_Parameter(DB.BuiltInParameter.PHASE_DEMOLISHED)

    # Shared parameters that will act as filters to infill type of walls (yes/no)
    wall_to_build = wall.LookupParameter('CONSTRUIR')
    wall_to_demolish = wall.LookupParameter('DEMOLIR')
    print(wall_to_demolish)
    # Filtering the elements and attributing the paramaters to the shared parameters check boxes
    if wall_phase_created.AsValueString() == 'Projeto':
        print('yes')
        t = DB.Transaction(doc, "applying ceiling finish material to room's parameter")
        t.Start()
        wall_to_build.Set(1)
        wall_to_demolish.Set(0)
        t.Commit()
    elif wall_phase_demolished.AsValueString() == 'Projeto':
        t = DB.Transaction(doc, "applying ceiling finish material to room's parameter")
        t.Start()
        wall_to_build.Set(0)
        wall_to_demolish.Set(1)
        t.Commit()

# NOTE:
# the alternative solution above uses check box/yes or no shared parameters' type. Though it is a more simple parameter
# to deal with at a first glance, compared to a text type, the latter may be less prone to error in day to day use, because
# the user can accidentally check none or both boxes at the same time, or uncheck the box of an element that should count as CONSTRUIR.
# This is exactly what needs to be avoided in the context of construction project budgets (leave out elements thant need
# to be inclujded in a certain budget) and precedes any optimizatyion/automation.
# To make this alternative error proof would.
# require making the parameters mutually exclusive (one == not(the_other)).
# As it requires more lines of code,
# it will be probably better to opt for two text parameters named CONSTRUIR and DEMOLIR that will receive, as input,
# the exact same text that is the name property of the PHASE_CREATED built-in parameter of each element (of wall, floor, or other
# constructyion element that will be quantified.


# ALTERNATIVE to either act as a double check or as a stand alone way to filter infill walls, which do not support profile sketch as "standard" wall elements do.
if wall.CanHaveProfileSketch == False:
    print('this wall is not being included')
    # ...
