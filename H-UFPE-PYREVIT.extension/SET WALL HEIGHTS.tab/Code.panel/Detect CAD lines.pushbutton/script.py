# -*- coding: utf-8 -*-
import clr

clr.AddReference('RevitAPI')
import Autodesk.Revit.DB as DB
import Autodesk.Revit.UI as UI

__title__     = "detect cad lines"
__author__    = "Hadassa Medeiros"
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

app = __revit__.Application
meter_to_double_factor = 3.28083989466

# collect all model lines (ImportInstance must be exploded to allow access to the CAD lines)
model_lines = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Lines).ToElements()

# wall_types_collector = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsElementType()
default_wall_type = None
wall_types_collector = DB.FilteredElementCollector(doc).OfClass(DB.WallType)

for wall_type in wall_types_collector:
    for param in wall_type.Parameters:
        # if p.Definition.Name == "Nome do tipo":
        if param.Definition.BuiltInParameter == DB.BuiltInParameter.ALL_MODEL_TYPE_NAME:
            wall_type_name = param.AsString()
            if wall_type_name == "ALV_9CM": #to be reviewed(use the least specific nomenclature possible)
                default_wall_type = wall_type        

level = DB.FilteredElementCollector(doc).OfClass(DB.Level).FirstElement()
print(level.Id)
if not level:
    print("No levels were found")

horizontal_lines = []
vertical_lines = []
unique_pairs = set()
default_wall_thickness = 0.492126 # equivalent to 150mm. To be refactored to include more wall thickness values

def find_line_pair(line_list, first_line):
    for line in line_list:
        # print(round(0.49212598425128817, 6))
        # print(round(abs(first_line.GeometryCurve.GetEndPoint(0)[1] - line.GeometryCurve.GetEndPoint(0)[1]), 6))
        if round(abs(first_line.GeometryCurve.GetEndPoint(0)[1] - line.GeometryCurve.GetEndPoint(0)[1]), 6) == default_wall_thickness:
            return frozenset([first_line, line])

for line in model_lines:
    if line.LineStyle.Name == "DPP-PAREDE" and line.GeometryCurve.IsBound:
        # level = line.SketchPlane #reference level through SketchPlane object's Name property(Name are supposedly equivalent in both objects)
        # print(line.GeometryCurve.GetEndPoint(0)[0])
        x_startpoint = line.GeometryCurve.GetEndPoint(0).X
        x_endpoint = line.GeometryCurve.GetEndPoint(1).X
        if x_startpoint - x_endpoint == 0:
            vertical_lines.append(line)
        else:
            # y_startpoint = line.GeometryCurve.GetEndPoint(0)[1]
            # y_endpoint = line.GeometryCurve.GetEndPoint(1)[1]
          
            y_startpoint = line.GeometryCurve.GetEndPoint(0).Y + (default_wall_thickness/2)
            y_endpoint = line.GeometryCurve.GetEndPoint(1).Y + (default_wall_thickness/2)
            # y_endpoint = line.GeometryCurve.GetEndPoint(1).Y
            horizontal_lines.append(line)
            # print(y_endpoint)

for horizontal_line in horizontal_lines:
    pair = find_line_pair(horizontal_lines, horizontal_line)
    # print(pair[0].GeometryCurve.GetEndPoint(0), '--------------------', pair[1].GeometryCurve.GetEndPoint(0))

    if pair is not None and pair not in unique_pairs:
        unique_pairs.add(pair)
        print(len(unique_pairs), "devem ser unicos no repetitions")
        line1, line2 = pair
        # print(line1.Id, '--', line1.GeometryCurve.GetEndPoint(0), '-------------------', line2.Id, '--', line2.GeometryCurve.GetEndPoint(0))

        if default_wall_type and level:
              # # ---------Below, the intention is to store a displaced value, as the start_point and end_point 
            # #, so that he wall is positioned at the center of the two lines that represent its external faces
            start_point = line1.GeometryCurve.GetEndPoint(0) + DB.XYZ(0, default_wall_thickness/2, 0)
            # print(start_point)
            end_point = line1.GeometryCurve.GetEndPoint(1) + DB.XYZ(0, default_wall_thickness/2, 0)
            bound_line = DB.Line.CreateBound(start_point, end_point)

            t = DB.Transaction(doc, "Create new wall instance from cad lines")
            t.Start()
            try:
                new_wall = DB.Wall.Create(doc, bound_line, default_wall_type.Id, level.Id, 10, 0, False, False)
                print("Wall created at {} and {}.".format(start_point, end_point))
            except Exception as e:
                print("Erro ao criar a parede: {}".format(e))
                pass
            t.Commit()
print('Ok')

# for l in vertical_lines:



