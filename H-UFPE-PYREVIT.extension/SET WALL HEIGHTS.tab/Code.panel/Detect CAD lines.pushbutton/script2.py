# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
import Autodesk.Revit.UI as UI
import clr
# import numpy as np

clr.AddReference('RevitAPI')


__title__     = "detect cad lines"
__author__    = "Hadassa Medeiros"
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

app = __revit__.Application
meter_to_double_factor = 3.28083989466

# collect all model lines (ImportInstance must be exploded to allow access to the CAD lines)
model_lines_collection = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Lines).ToElements()

# wall_types_collector = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsElementType()
default_wall_type = None
wall_types_collector = DB.FilteredElementCollector(doc).OfClass(DB.WallType)

for wall_type in wall_types_collector:
    for param in wall_type.Parameters:
        # if p.Definition.Name == "Nome do tipo":
        if param.Definition.BuiltInParameter == DB.BuiltInParameter.ALL_MODEL_TYPE_NAME:
            if param.AsString() == "ALV_9CM": #to be reviewed(use the least specific nomenclature possible)
                default_wall_type = wall_type        

level = DB.FilteredElementCollector(doc).OfClass(DB.Level).FirstElement()
if not level:
    print("No levels were found")

horizontal_lines = []
vertical_lines = []

parallel_lines_pair = ()
lines_to_consider = []

default_wall_thickness = 0.492126 # equivalent to 150mm. To be refactored to include more wall thickness values
# # to be continued:
def get_startpoint(model_line, axis):
    if axis == 'y':
        return model_line.GeometryCurve.GetEndPoint(0).Y
    elif axis == 'x':
        return model_line.GeometryCurve.GetEndPoint(0).X

def get_endpoint(model_line, axis):
    if axis == 'y':
            return model_line.GeometryCurve.GetEndPoint(1).Y
    elif axis == 'x':
        return model_line.GeometryCurve.GetEndPoint(1).X
    
# def lines_intersect(lineA, lineB):
#     # all_points_in_lineA = np.linspace(get_startpoint(lineA,'y'), get_endpoint(lineA,'y'), num=4)
# # (get_startpoint(lineA,'y') - get_endpoint(lineA,'y'))
#     print(len(all_points_in_lineA))
#     if all_points_in_lineA > 0:
#         return True
#     else:
#         return False

def lines_represent_same_wall(line_1, line_2, axis):
        # 1st filter: horizontal or vertical
        start_1 = abs(get_startpoint(line_1, 'x'))
        end_1 = abs(get_endpoint(line_1, 'x'))
        # start_y_1 = line_1.GeometryCurve.GetEndPoint(0).Y
        # end_y_1 = line_1.GeometryCurve.GetEndPoint(1).Y

        start_2 = abs(get_startpoint(line_2, 'x'))
        end_2 = abs(get_endpoint(line_2, 'x'))
        # start_x_2 = line_2.GeometryCurve.GetEndPoint(0).X
        # end_x_2 = line_2.GeometryCurve.GetEndPoint(1).X
        # start_y_2 = line_2.GeometryCurve.GetEndPoint(0).Y
        # end_y_2 = line_2.GeometryCurve.GetEndPoint(1).Y  
        print(line_1.Id, start_1, end_1, '---', line_2.Id, start_2, end_2)          
        if ((start_1 or end_1) > start_2) and ((start_1 or end_1) < end_2):
            print(line_1.Id, line_2.Id)
            return True
        else:
            # print(start_1)
            return False
                
# def find_line_pair(line_list, ref_line, axis):
def find_line_pair(line_list, ref_line):
    for line in line_list:
        lines_represent_same_wall(line, ref_line, 'y')
        # checks if distance between parallel lines equals wall thickness:
        if round(
            abs(
                get_startpoint(ref_line,'y') - get_startpoint(line,'y')
                ), 6
            ) == default_wall_thickness:
            # ) == default_wall_thickness and lines_represent_same_wall(line, ref_line, 'y'):
                # print(line)
                # line_list.remove(line)
                return (ref_line, line)
 
for line in model_lines_collection:
    if line.LineStyle.Name == "DPP-PAREDE" and line.GeometryCurve.IsBound:
        # print(line.Id)
        # level = line.SketchPlane #reference level through SketchPlane object's Name property(Name are supposedly equivalent in both objects)
        # print(line.GeometryCurve.GetEndPoint(0)[0])
        start_x = line.GeometryCurve.GetEndPoint(0).X
        end_x = line.GeometryCurve.GetEndPoint(1).X
        start_y = line.GeometryCurve.GetEndPoint(0).Y
        end_y = line.GeometryCurve.GetEndPoint(1).Y

        b = start_y + (default_wall_thickness/2)
        # print(start_y, end_y)
        if start_y - end_y == 0:
            horizontal_lines.append(line)
        else:
            vertical_lines.append(line)

# horizontal_lines_set = set(horizontal_lines)

# for horizontal_line in horizontal_lines:
#     pair = find_line_pair(horizontal_lines, horizontal_line)
#     if pair:
#         line1, line2 = pair
#         # print(line1.Id, line2.Id)
# # append cada par em uma lista grande tipo [[a,b], [b,a]] e achar um jeito de
# # eliminar duplicados pra considerar APENAS UMA DAS LINHAS de cada par.
#         if default_wall_type and level:
#               # # ---------Below, the intention is to store a displaced value, as the start_point and end_point 
#             # #, so that he wall is positioned at the center of the two lines that represent its external faces
#             start_point = line1.GeometryCurve.GetEndPoint(0) + DB.XYZ(0, default_wall_thickness/2, 0)
#             end_point = line1.GeometryCurve.GetEndPoint(1) + DB.XYZ(0, default_wall_thickness/2, 0)
#             bound_line = DB.Line.CreateBound(start_point, end_point)

#             t = DB.Transaction(doc, "Create new wall instance from cad lines")
#             t.Start()
#             try:
#                 new_wall = DB.Wall.Create(doc, bound_line, default_wall_type.Id, level.Id, 10, 0, False, False)
#                 print("Wall created at {} and {}.".format(start_point, end_point))
#             except Exception as e:
#                 print("Erro ao criar a parede: {}".format(e))
#                 pass
#             t.Commit()

