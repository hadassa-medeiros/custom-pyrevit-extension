# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from revit_doc_interface import (RevitDocInterface, ModelLine, get_ids_of, get_name, get_names)

doc = __revit__.ActiveUIDocument.Document
collect = DB.FilteredElementCollector(doc)

interface = RevitDocInterface()

get_names(interface.walltypes)
# agrupar linhas verticais e horizontais
default_wall_thickness = 0.492126 # equivalent to 150mm. To be refactored to include more wall thickness values
default_wall_type_name = "GENERICA_15CM"

horizontal_lines = []
vertical_lines = []

        
# get_wall_layer_lines(interface.model_lines, cad_wall_layer_names)
            # line = ModelLine(line)
cad_wall_layer_lines= interface.filter_lines_by_name(["Parede"])
# for line in cad_wall_layer_lines:
    
    
    #wall_faces = [lineA, lineB]
    # detectar pares e me devolver apenas linha q interessa(ou seja: 1 que representa uma mesma parede q a linha irmã e length> twin_line)
    
    





# for wall_type in wall_types_collector:
#     for param in wall_type.Parameters:
#         # if p.Definition.Name == "Nome do tipo":
#         if param.Definition.BuiltInParameter == DB.BuiltInParameter.ALL_MODEL_TYPE_NAME:
#             if param.AsString() == "ALV_9CM": #to be reviewed(use the least specific nomenclature possible)
#                 default_wall_type = wall_type        
        
        
        
# def create_wall(doc, bound_line, default_wall_type_id, level_id, misterious_1 = 10, misterious_2 = 0 , flag_1 = False, flag_2 = False):
#     # def create_wall(doc, bound_line, default_wall_type.Id, level.Id, 10, 0 , False, False):
#     t = DB.Transaction(doc, "Create new wall instance from cad lines")
#     t.Start()
#     try:
#         DB.Wall.Create(doc, bound_line, default_wall_type_id, level_id, 10, 0, False, False)
#         # print("Wall created at {} and {}.".format(start_point, end_point))
#     except Exception as e:
#         print("Erro ao criar a parede: {}".format(e))
#         pass
#     t.Commit()

# # def lines_intersect(line_)
# def lines_represent_same_wall(line_list, main_axis, aux_axis):
#     while len(line_list) > 1:
#         line_1 = line_list[0]
#         start_1 = startpoint(line_1, main_axis)
#         end_1 = endpoint(line_1, main_axis)
        
#         intersecting_lines = [line_1]
#         wall_delimiting_faces = [line_1.Id.ToString()]
        
#         for i in range(1, len(line_list)):
#             line_2 = line_list[i]
#             start_2 = startpoint(line_2, main_axis)
#             end_2 = endpoint(line_2, main_axis)
            
#             if main_axis == 'y':
#                 if (
#                     (start_1 >= start_2 >= end_1) or 
#                     (start_1 >= end_2 >= end_1) or 
#                     (start_2 >= start_1 >= end_2) or 
#                     (start_2 >= end_1 >= end_2) or 
#                     ((start_1 == start_2 and end_1 == end_2) or (start_1 == end_2 and end_1 == start_2))
#                 ):
#                     print("lines {} {} intersect in at least one point.".format(line_1.Id, line_2.Id))
#                     intersecting_lines.append(line_2)
                    
#                     startpoint_wall_face_A = startpoint(line_1, aux_axis)
#                     startpoint_wall_face_B = startpoint(line_2, aux_axis)
#                     endpoint_wall_face_A = endpoint(line_1, aux_axis)
#                     endpoint_wall_face_B = endpoint(line_2, aux_axis)
                    
#                     dist_between_faces_startpoints = round(abs(startpoint_wall_face_B - startpoint_wall_face_A), 6)
#                     dist_between_faces_endpoints = round(abs(endpoint_wall_face_B - endpoint_wall_face_A), 6)

#                     if dist_between_faces_startpoints and dist_between_faces_endpoints == default_wall_thickness:
#                         wall_delimiting_faces.append(line_2)
#                         for face in wall_delimiting_faces:
#                             print(face.GeometryCurve.length())
                        
#             if main_axis == 'x':
#                 if (
#                     (start_1 <= start_2 <= end_1) or 
#                     (start_1 <= end_2 <= end_1) or 
#                     (start_2 <= start_1 <= end_2) or 
#                     (start_2 <= end_1 <= end_2) or 
#                     ((start_1 == start_2 and end_1 == end_2) or (start_1 == end_2 and end_1 == start_2))
#                 ):
#                     print("lines {} {} intersect in at least one point.".format(line_1.Id, line_2.Id))
#                     intersecting_lines.append(line_2)
                    
#                     startpoint_wall_face_A = startpoint(line_1, aux_axis)
#                     startpoint_wall_face_B = startpoint(line_2, aux_axis)
#                     endpoint_wall_face_A = endpoint(line_1, aux_axis)
#                     endpoint_wall_face_B = endpoint(line_2, aux_axis)
                    
#                     dist_between_faces_startpoints = round(abs(startpoint_wall_face_B - startpoint_wall_face_A), 6)
#                     dist_between_faces_endpoints = round(abs(endpoint_wall_face_B - endpoint_wall_face_A), 6)

#                     if dist_between_faces_startpoints and dist_between_faces_endpoints == default_wall_thickness:
#                         print(dist_between_faces_startpoints, dist_between_faces_endpoints,'bla')
#                         wall_delimiting_faces.append(line_2)
#                         # print(wall_delimiting_faces)
#                         a = line_1.GeometryCurve.GetEndPoint(0) - DB.XYZ(0, default_wall_thickness/2, 0)
#                         b = line_1.GeometryCurve.GetEndPoint(1) - DB.XYZ(0, default_wall_thickness/2, 0)
#                         bound_line = DB.Line.CreateBound(a, b)
#                         # como prever casos em que uma mesma parede é conformada por várias linhas curtas/interruptas e recolher apenas uma das linhas (a maior), para inserir a parede com base nela apenas?
#                         create_wall(doc, bound_line, default_wall_type.Id, level.Id, 10, 0 , False, False)
#         line_list.pop(0)

# tolerance = 1e-6 

# for line in model_lines_collection:
#     if any(name in line.LineStyle.Name for name in cad_wall_layer_names):
#         x_startpoint = line.GeometryCurve.GetEndPoint(0).X
#         x_endpoint = line.GeometryCurve.GetEndPoint(1).X
#         y_startpoint = line.GeometryCurve.GetEndPoint(0).Y
#         y_endpoint = line.GeometryCurve.GetEndPoint(1).Y

#         # if line.GeometryCurve.Length == abs(x_endpoint - x_startpoint):
#         #     print("linha reta")
#         # print(abs(x_endpoint - x_startpoint))
#         # print(line.GeometryCurve.Length)

#         if abs(x_endpoint - x_startpoint) < tolerance:
#             vertical_lines.append(line)
        
#         if abs(y_endpoint - y_startpoint) < tolerance:
#             horizontal_lines.append(line)

# # for linha in linhas horizontais
# #     encontrar as que rDepresentam uma mesma parede e fazer um par
# grouped_lines = [horizontal_lines, vertical_lines]

# lines_represent_same_wall(vertical_lines, 'y', 'x')
# lines_represent_same_wall(horizontal_lines, 'x', 'y')

# # for linha in linhas verticais
# #     encontrar as que representam uma mesma parede e fazer um par
# # for par in pares
# #     encontrar linha maior e mostrar se ela esta acima ou abaixo da menor
# #     if linha maior is acima
# #         adicionar parede abaixo
# #     else
# #         adicionar parede acima


#     # wma = []
#     # for i in range(len(prices) - len(weights) + 1):
#     #     weighted_sum = sum(prices[i + j] * normalized_weights[j] for j in range(len(weights)))
#     #     wma.append(weighted_sum)
    
    
# # def lines_represent_same_wall(line_list):
# # # print(len(line_list))
# #     i = 0
# #     while i < (len(line_list) - 1):
# #     # print(line_list[i].GeometryCurve.Length < line_2.GeometryCurve.Length, line_list[i].Id)
# #         print(line_list[i].GeometryCurve.Length, 'less than', line_2.GeometryCurve.Length)
# #         i += 1  