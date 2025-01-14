# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from revit_doc_interface import (RevitDocInterface, ModelLine, find_id_by_element_name, get_name, get_names, meter_to_double)
import math

doc = __revit__.ActiveUIDocument.Document
collect = DB.FilteredElementCollector(doc)

interface = RevitDocInterface()

# find groups of lines that represent the faces of a same wall and store them
default_wall_thickness = meter_to_double(0.15)
# print(default_wall_thickness)
default_walltype_id = find_id_by_element_name(interface.walltypes, "GENERICA_15CM")

cad_wall_lines = interface.filter_lines_by_name(["Parede"])
tolerance = 1e-5

def is_horizontal(model_line):
    return abs(model_line.end_y - model_line.start_y) == 0

def is_vertical(model_line):
    return abs(model_line.end_x - model_line.start_x) == 0

def is_diagonal(model_line):
    return model_line.end_x - model_line.start_x != 0 and model_line.end_y - model_line.start_y != 0

def offset_equals_wall_width(line_A, line_B):
    def dist_between_lines():
        if is_horizontal(line_B) and is_horizontal(line_A):
            offset = (abs(line_B.start_y - line_A.start_y))
        elif is_vertical(line_B) and is_vertical(line_A):
            offset = (abs(line_B.start_x - line_A.start_x))
        else:
            offset = 0
        return offset
    if (dist_between_lines() - default_wall_thickness) < tolerance:
        return True
    else:
        return False

def are_parallel(line_A, line_B):
    #two given lines must share the same plane (level elevation) and be equidistant at any point
    start_A = line_A.start_point
    end_A = line_A.end_point
    start_B = line_B.start_point
    end_B = line_B.end_point

    lines_share_same_plane = abs(start_A.Z - start_B.Z) < 1e-6
   
    # Calcula os vetores diretores
    vector_A = end_A - start_A
    vector_B = end_B - start_B
    
    cross_product = vector_A.CrossProduct(vector_B)
    # Verifica se o comprimento do vetor cruzado é quase zero (linhas perfeitamente paralelas)
    if cross_product.IsZeroLength():
        is_parallel = True
    else:
        # Para diagonais ou imprecisões, verifica se o comprimento do produto vetorial é pequeno (< 1)
        is_parallel = cross_product.GetLength() < .4

    # Retorna verdadeiro se as linhas estiverem no mesmo plano e forem paralelas
    return lines_share_same_plane and is_parallel

def share_point_in_perpendicular_axis(line_A, line_B):
    # for two given lines, checks if they share a common point in the opposite axis
    # to that in which they're located as straight horizontal (x) ou vertical (y) lines.
    # This means they probably represent two faces of a same wall, if wall_thickness 
    # condition is also true.
    if is_horizontal(line_A) and is_horizontal(line_B):
        if (
            line_B.start_x <= line_A.start_x <= line_B.end_x
        ) or (
            line_A.start_x <= line_B.start_x <= line_A.end_x
        ) or (
            line_B.end_x <= line_A.end_x <= line_B.start_x
        ) or (
            line_A.end_x <= line_B.end_x <= line_A.start_x
        ):
            return True
    elif is_vertical(line_A) and is_vertical(line_B):
        if (
            line_B.start_y >= line_A.start_y >= line_B.end_y
        ) or (
            line_A.start_y >= line_B.start_y >= line_A.end_y
        ) or (
            line_B.end_y >= line_A.end_y >= line_B.start_y
        ) or (
            line_A.end_y >= line_B.end_y >= line_A.start_y
        ):
            return True
    elif is_diagonal(line_A) and is_diagonal(line_B):
        return True
    return False

grouped_lines = []

i = 0
for i in range(len(cad_wall_lines)-1):
    n = i+1
    ref_line = ModelLine(cad_wall_lines[i])
    lines_of_same_wall = [ref_line]
    while n < len(cad_wall_lines):
        next_line = ModelLine(cad_wall_lines[n])
        # print('comparing now {} to {}:'.format(str(cad_wall_lines[i].Id), str(cad_wall_lines[n].Id)))
        # print(share_point_in_perpendicular_axis(ref_line, next_line))
        # print(offset_equals_wall_width(ref_line, next_line))
        # print(are_parallel(ref_line, next_line))
        if are_parallel(
                ref_line, next_line
            ) and offset_equals_wall_width(
                ref_line, next_line
            ) and share_point_in_perpendicular_axis(
                ref_line, next_line
            ):
            lines_of_same_wall.append(next_line)
        # print(len(lines_of_same_wall))
        n+=1
    if len(lines_of_same_wall) > 1:
        grouped_lines.append(lines_of_same_wall)
    i+=1

print(grouped_lines)

def create_wall(doc, bound_line, default_wall_type_id, level_id, misterious_param_1 = 10, misterious_param_2 = 1, flag_1 = False, flag_2 = False):
    t = DB.Transaction(doc, "Create new wall instance from cad line")
    t.Start()
    try:
        wall = DB.Wall.Create(doc, bound_line, default_wall_type_id, level_id, 10, 0, False, False)
        wall_location_line = wall.get_Parameter(DB.BuiltInParameter.WALL_KEY_REF_PARAM)
        if wall_location_line and wall_location_line.IsReadOnly == False:
            wall_location_line.Set(0)  # Define Linha central da parede como Linha de localizacao
    except Exception as e:
        print("Error creating wall instance: {}".format(e))
        pass
    t.Commit()

# print(grouped_lines)

def longest(line_list):
    if line_list[0].length > lines[1].length:
        longest = line_list[0]
    else:
        longest = line_list[1]
    return longest

def shortest_or_equal(line_list):
    if line_list[0].length < lines[1].length:
        shortest = line_list[0]
    else:
        shortest = line_list[1]
    return shortest

def equal_length(line_list):
    if (line_list[0].length - lines[1].length) < tolerance:
        return line_list[0]
    else:
        return line_list[1]

for lines in grouped_lines:
    ref_line = longest(lines) or equal_length(lines)
    aux_line = shortest_or_equal(lines)
    # ref_line = shortest(lines)
    # aux_line = longest(lines)
    # # determine line positioning condition relative to the other(s) in the same group
    print(ref_line.start_x, aux_line.start_x)
    is_right = is_vertical(ref_line) and ref_line.start_x > aux_line.start_x
    is_left = is_vertical(ref_line) and ref_line.start_x < aux_line.start_x
    # print(is_right, is_vertical(ref_line), 'must be opposite of', is_left)
    is_above = is_horizontal(ref_line) and ref_line.start_y > aux_line.start_y
    is_below = is_horizontal(ref_line) and ref_line.start_y < aux_line.start_y

    if is_right:
        a = ref_line.start_point - DB.XYZ(default_wall_thickness/2, 0, 0)
        b = ref_line.end_point - DB.XYZ(default_wall_thickness/2, 0, 0)
    elif is_left:
        a = ref_line.start_point + DB.XYZ(default_wall_thickness/2, 0, 0)
        b = ref_line.end_point + DB.XYZ(default_wall_thickness/2, 0, 0)
    elif is_above:
        a = ref_line.start_point - DB.XYZ(0, default_wall_thickness/2, 0)
        b = ref_line.end_point - DB.XYZ(0, default_wall_thickness/2, 0)
    elif is_below:
        a = ref_line.start_point + DB.XYZ(0, default_wall_thickness/2, 0)
        b = ref_line.end_point + DB.XYZ(0, default_wall_thickness/2, 0)
    else:
        a = ref_line.start_point + DB.XYZ(0, 0, 0)
        b = ref_line.end_point + DB.XYZ(0, 0, 0)
    try:
        bound_line = DB.Line.CreateBound(a, b)
        create_wall(doc, bound_line, default_walltype_id, interface.levels[0].Id, 10, 0, False, False)
    except NameError as e:
        print(e)
        pass