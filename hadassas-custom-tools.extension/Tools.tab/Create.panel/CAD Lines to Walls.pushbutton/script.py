# # -*- coding: utf-8 -*-
# import Autodesk.Revit.DB as DB
# from revit_doc_interface import (RevitDocInterface, get_elem_param)

# wall_lines = []

# def get_line_layer_param(line):
#     """Get the BUILDING_CURVE_GSTYLE parameter from a line."""
#     return line.get_Parameter(DB.BuiltInParameter.BUILDING_CURVE_GSTYLE).AsValueString()

# doc = __revit__.ActiveUIDocument.Document
# interface = RevitDocInterface()
# # access lines of layer Paredes from imported CAD file
# def get_cad_lines_to_walls():
#     cad_lines = interface.lines
#     print('cad_lines:', cad_lines)

#     return cad_lines

# for line in get_cad_lines_to_walls():
#     elem_param = get_line_layer_param(line)
#     if elem_param == 'Parede':
#         wall_lines.append(line)

# # get any elementid from any walltype
# def get_wall_type():
#     wall_types = DB.FilteredElementCollector(doc).OfClass(DB.WallType).ToElements()
#     if wall_types:
#         return wall_types[0].Id  # Return the first wall type found
#     return None

# def get_level_id():
#     """Get the first level ID from the document."""
#     levels = DB.FilteredElementCollector(doc).OfClass(DB.Level).ToElements()
#     if levels:
#         return levels[0].Id  # Return the first level found
#     return None

# def create_walls_from_line():
#     t = DB.Transaction(doc, "Create Wall from Line")
#     line = wall_lines[0]  # Assuming we want to create a wall from the first line found
#     walltype_id = get_wall_type()
#     level_id = get_level_id()
#     t.Start()   
#     DB.Wall.Create(doc, line.GeometryCurve, walltype_id, level_id, False)
#     t.Commit()
#     print('Wall created from line:', line.Id)

# create_walls_from_line()

# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from revit_doc_interface import (RevitDocInterface, ModelLine, find_id_by_element_name, get_name, get_names, metric_to_double)
import unicodedata

def normalize_string(input_string):
    return unicodedata.normalize('NFKD', input_string).encode('ASCII', 'ignore').decode('ASCII')

doc = __revit__.ActiveUIDocument.Document

interface = RevitDocInterface()
# find groups of lines that represent the faces of a same wall and store them
default_wall_width = metric_to_double(0.20)

def default_wall_widths(list_of_common_wall_widths):
    return [metric_to_double(common_w) for common_w in list_of_common_wall_widths]

print(default_wall_widths([0.15, 0.20, 0.25, 0.30]))

def get_wall_type():
    wall_types = DB.FilteredElementCollector(doc).OfClass(DB.WallType).ToElements()
    if wall_types:
        return wall_types[0].Id  # Return the first wall type found
    return None
cad_wall_lines = interface.filter_lines_by_name(["Parede"])

tolerance = default_wall_width * 0.05 #allows +/- 2% variation to account for minor CAD drawing imprecisions

def is_horizontal(model_line):
    return abs(model_line.end_y - model_line.start_y) == 0

def is_vertical(model_line):
    return abs(model_line.end_x - model_line.start_x) == 0

def is_diagonal(model_line):
    return model_line.end_x - model_line.start_x != 0 and model_line.end_y - model_line.start_y != 0

def offset_equals_wall_width(line_A, line_B):
    def dist_between_lines():
        if is_horizontal(line_B) and is_horizontal(line_A):
            return abs(line_B.start_y - line_A.start_y)
        elif is_vertical(line_B) and is_vertical(line_A):
            return abs(line_B.start_x - line_A.start_x)
        # elif is_diagonal(line_A) and is_diagonal(line_B):
            
        else:
            return default_wall_width
    offset = dist_between_lines()
    if abs(offset - default_wall_width) < tolerance:
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
for l in interface.levels:
    print(l.Id)

for i in range(len(cad_wall_lines)):
    def lines_have_minimum_length(line_A, line_B):
        min_length = default_wall_width*2.5
        def line_length(line):
            return line.get_Parameter(DB.BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble()
        # print(line_length(line_A), line_length(line_B))
        return line_length(line_A) >= min_length and line_length(line_B) >= min_length
    
    ref_line = ModelLine(cad_wall_lines[i])
    lines_of_same_wall = [ref_line]
    # def line_level_id(line):
    #     line_sketch_plane = line.get_Parameter(DB.BuiltInParameter.SKETCH_PLANE_PARAM).AsString()
    #     linel_level_name = line_sketch_plane.split()[-1]
    #     linel_level_name = normalize_string(linel_level_name)  # Normaliza a string para remover acentos

    #     for level in interface.levels:
    #         print((normalize_string(level.Name) == linel_level_name)
    #         line_level_id = level.Id if linel_level_name == normalize_string(level.Name) else None
    #     print(linel_level_name, line_level_id)
    #     return line_level_id

    # line_level_id(cad_wall_lines[i])

    n = i+1
    while n < len(cad_wall_lines):
        next_line = ModelLine(cad_wall_lines[n])
        print('comparing now {} to {}:'.format(str(cad_wall_lines[i].Id), str(cad_wall_lines[n].Id)))
        print('have intersecting points?', share_point_in_perpendicular_axis(ref_line, next_line))
        print('offset equals width?', offset_equals_wall_width(ref_line, next_line))
        print('parallel?', are_parallel(ref_line, next_line))
        print(lines_have_minimum_length(cad_wall_lines[i], cad_wall_lines[n]))
        if (
            are_parallel(ref_line, next_line)
            # and offset_equals_wall_width(ref_line, next_line)
            # and share_point_in_perpendicular_axis(ref_line, next_line)
            # and lines_have_minimum_length(cad_wall_lines[i], cad_wall_lines[n])
        ):
            lines_of_same_wall.append(next_line)
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

def equal_length(line_list):
    if (line_list[0].length - lines[1].length) < tolerance:
        return line_list[0]
    else:
        return line_list[1]

for lines in grouped_lines:
    # Ordena as linhas do grupo pelo menor ponto inicial (start_x, start_y)
    sorted_lines = sorted(
        lines,
        key=lambda line: (line.start_x, line.start_y)
    )
    # print(sorted_lines)
    # Seleciona a primeira como linha de referência e a segunda como linha auxiliar
    ref_line = sorted_lines[0]
    aux_line = sorted_lines[1]
    # print(ref_line.start_x, aux_line.start_x)
    # Vetores direção para linha de referência
    ref_dir = DB.XYZ(ref_line.end_x - ref_line.start_x, ref_line.end_y - ref_line.start_y, 0)
    
    # Determina deslocamento para criar a linha entre as duas
    offset_x = default_wall_width / 2 if abs(ref_dir.X) < abs(ref_dir.Y) else 0
    offset_y = default_wall_width / 2 if abs(ref_dir.Y) < abs(ref_dir.X) else 0

    # Ajusta deslocamento com base na posição relativa
    if aux_line.start_x > ref_line.start_x:  # Auxiliar à direita
        offset_x *= -1
    if aux_line.start_y > ref_line.start_y:  # Auxiliar acima
        offset_y *= -1

    # Cria os novos pontos deslocados
    a = ref_line.start_point - DB.XYZ(offset_x, offset_y, 0)
    b = ref_line.end_point - DB.XYZ(offset_x, offset_y, 0)
    

    try:
        bound_line = DB.Line.CreateBound(a, b)
        print(bound_line)
         # Cria a parede com a linha deslocada
        create_wall(doc, bound_line, get_wall_type(), interface.levels[0].Id, 10, 0, False, False)
    except NameError as e:
        print("Erro ao criar parede: {}".format(e))