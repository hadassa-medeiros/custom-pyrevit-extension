# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
doc = __revit__.ActiveUIDocument.Document

# guardar todas as linhas
collect = DB.FilteredElementCollector(doc)
model_lines_collection = collect.OfCategory(DB.BuiltInCategory.OST_Lines).ToElements()

cad_wall_layer_names = ["parede".capitalize(), "parede".upper()]
# agrupar linhas verticais e horizontais
default_wall_thickness = 0.492126 # equivalent to 150mm. To be refactored to include more wall thickness values

horizontal_lines = []
vertical_lines = []

ModelLines = 
class Point:
    def __init__(self, RevitDBObject):
        self.x = RevitDBObject.X
        self.y = RevitDBObject.Y


class Line:
    def __init__(self, RevitOBJ: ModelLines):
        self.start_point = Point(RevitOBJ.GeometryCurve.GetEndPoint(0))
        self.end_point = Point(RevitOBJ.GeometryCurve.GetEndPoint(1))
    
    @property
    def start_x(self):
        return self.start_point.X
    
    @property
    def start_y(self):
        return self.start_point.X

    @property
    def end_x(self):
        return self.end_point.X

    @property
    def end_y(self):
        return self.end_point.X


# COmeço do script final
# criar objetos com classes próprias
#     paredes = load_paredes(arquivo)
#

def startpoint(model_line, axis):
    if axis == 'y':
        return model_line.GeometryCurve.GetEndPoint(0).Y
    elif axis == 'x':
        return model_line.GeometryCurve.GetEndPoint(0).X

def endpoint(model_line, axis):
    if axis == 'y':
        return model_line.GeometryCurve.GetEndPoint(1).Y
    elif axis == 'x':
        return model_line.GeometryCurve.GetEndPoint(1).X
    
default_wall_type = None
wall_types_collector = DB.FilteredElementCollector(doc).OfClass(DB.WallType)

for wall_type in wall_types_collector:
    for param in wall_type.Parameters:
        # if p.Definition.Name == "Nome do tipo":
        if param.Definition.BuiltInParameter == DB.BuiltInParameter.ALL_MODEL_TYPE_NAME:
            if param.AsString() == "ALV_9CM": #to be reviewed(use the least specific nomenclature possible)
                default_wall_type = wall_type
                
level = DB.FilteredElementCollector(doc).OfClass(DB.Level).FirstElement()
        
        
        
        
def create_wall(doc, bound_line, default_wall_type_id, level_id, 10, 0 , False, False):
    # def create_wall(doc, bound_line, default_wall_type.Id, level.Id, 10, 0 , False, False):
    t = DB.Transaction(doc, "Create new wall instance from cad lines")
    t.Start()
    try:
        DB.Wall.Create(doc, bound_line, default_wall_type_id, level_id, 10, 0, False, False)
        # print("Wall created at {} and {}.".format(start_point, end_point))
    except Exception as e:
        print("Erro ao criar a parede: {}".format(e))
        pass
    t.Commit()

# def lines_intersect(line_)
def lines_represent_same_wall(line_list, main_axis, aux_axis):
    while len(line_list) > 1:
        line_1 = line_list[0]
        start_1 = startpoint(line_1, main_axis)
        end_1 = endpoint(line_1, main_axis)
        
        intersecting_lines = [line_1]
        wall_delimiting_faces = [line_1.Id.ToString()]
        
        for i in range(1, len(line_list)):
            line_2 = line_list[i]
            start_2 = startpoint(line_2, main_axis)
            end_2 = endpoint(line_2, main_axis)
            
            if main_axis == 'y':
                if (
                    (start_1 >= start_2 >= end_1) or 
                    (start_1 >= end_2 >= end_1) or 
                    (start_2 >= start_1 >= end_2) or 
                    (start_2 >= end_1 >= end_2) or 
                    ((start_1 == start_2 and end_1 == end_2) or (start_1 == end_2 and end_1 == start_2))
                ):
                    print("lines {} {} intersect in at least one point.".format(line_1.Id, line_2.Id))
                    intersecting_lines.append(line_2)
                    
                    startpoint_wall_face_A = startpoint(line_1, aux_axis)
                    startpoint_wall_face_B = startpoint(line_2, aux_axis)
                    endpoint_wall_face_A = endpoint(line_1, aux_axis)
                    endpoint_wall_face_B = endpoint(line_2, aux_axis)
                    
                    dist_between_faces_startpoints = round(abs(startpoint_wall_face_B - startpoint_wall_face_A), 6)
                    dist_between_faces_endpoints = round(abs(endpoint_wall_face_B - endpoint_wall_face_A), 6)

                    if dist_between_faces_startpoints and dist_between_faces_endpoints == default_wall_thickness:
                        wall_delimiting_faces.append(line_2)
                        for face in wall_delimiting_faces:
                            print(face.GeometryCurve.length())
                        
            if main_axis == 'x':
                if (
                    (start_1 <= start_2 <= end_1) or 
                    (start_1 <= end_2 <= end_1) or 
                    (start_2 <= start_1 <= end_2) or 
                    (start_2 <= end_1 <= end_2) or 
                    ((start_1 == start_2 and end_1 == end_2) or (start_1 == end_2 and end_1 == start_2))
                ):
                    print("lines {} {} intersect in at least one point.".format(line_1.Id, line_2.Id))
                    intersecting_lines.append(line_2)
                    
                    startpoint_wall_face_A = startpoint(line_1, aux_axis)
                    startpoint_wall_face_B = startpoint(line_2, aux_axis)
                    endpoint_wall_face_A = endpoint(line_1, aux_axis)
                    endpoint_wall_face_B = endpoint(line_2, aux_axis)
                    
                    dist_between_faces_startpoints = round(abs(startpoint_wall_face_B - startpoint_wall_face_A), 6)
                    dist_between_faces_endpoints = round(abs(endpoint_wall_face_B - endpoint_wall_face_A), 6)

                    if dist_between_faces_startpoints and dist_between_faces_endpoints == default_wall_thickness:
                        print(dist_between_faces_startpoints, dist_between_faces_endpoints,'bla')
                        wall_delimiting_faces.append(line_2)
                        # print(wall_delimiting_faces)
                        a = line_1.GeometryCurve.GetEndPoint(0) - DB.XYZ(0, default_wall_thickness/2, 0)
                        b = line_1.GeometryCurve.GetEndPoint(1) - DB.XYZ(0, default_wall_thickness/2, 0)
                        bound_line = DB.Line.CreateBound(a, b)
                        # como prever casos em que uma mesma parede é conformada por várias linhas curtas/interruptas e recolher apenas uma das linhas (a maior), para inserir a parede com base nela apenas?
                        create_wall(doc, bound_line, default_wall_type.Id, level.Id, 10, 0 , False, False)
                        t = DB.Transaction(doc, "Create new wall instance from cad lines")
                        t.Start()
                        try:
                            DB.Wall.Create(doc, bound_line, default_wall_type.Id, level.Id, 10, 0, False, False)
                            # print("Wall created at {} and {}.".format(start_point, end_point))
                        except Exception as e:
                            print("Erro ao criar a parede: {}".format(e))
                            pass
                        t.Commit()
        line_list.pop(0)

tolerance = 1e-6 

for line in model_lines_collection:
    if any(name in line.LineStyle.Name for name in cad_wall_layer_names):
        x_startpoint = line.GeometryCurve.GetEndPoint(0).X
        x_endpoint = line.GeometryCurve.GetEndPoint(1).X
        y_startpoint = line.GeometryCurve.GetEndPoint(0).Y
        y_endpoint = line.GeometryCurve.GetEndPoint(1).Y

        # if line.GeometryCurve.Length == abs(x_endpoint - x_startpoint):
        #     print("linha reta")
        # print(abs(x_endpoint - x_startpoint))
        # print(line.GeometryCurve.Length)

        if abs(x_endpoint - x_startpoint) < tolerance:
            vertical_lines.append(line)
        
        if abs(y_endpoint - y_startpoint) < tolerance:
            horizontal_lines.append(line)

# for linha in linhas horizontais
#     encontrar as que rDepresentam uma mesma parede e fazer um par
grouped_lines = [horizontal_lines, vertical_lines]

lines_represent_same_wall(vertical_lines, 'y', 'x')
lines_represent_same_wall(horizontal_lines, 'x', 'y')

# for linha in linhas verticais
#     encontrar as que representam uma mesma parede e fazer um par
# for par in pares
#     encontrar linha maior e mostrar se ela esta acima ou abaixo da menor
#     if linha maior is acima
#         adicionar parede abaixo
#     else
#         adicionar parede acima


    # wma = []
    # for i in range(len(prices) - len(weights) + 1):
    #     weighted_sum = sum(prices[i + j] * normalized_weights[j] for j in range(len(weights)))
    #     wma.append(weighted_sum)
    
    
# def lines_represent_same_wall(line_list):
# # print(len(line_list))
#     i = 0
#     while i < (len(line_list) - 1):
#     # print(line_list[i].GeometryCurve.Length < line_2.GeometryCurve.Length, line_list[i].Id)
#         print(line_list[i].GeometryCurve.Length, 'less than', line_2.GeometryCurve.Length)
#         i += 1  