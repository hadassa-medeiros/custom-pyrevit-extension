# -*- coding: utf-8 -*-
import Autodesk.Revit as Revit
import Autodesk.Revit.DB as db
from lib import Convert, Model
from pyrevit import forms
import itertools
# from Autodesk.Revit.UI import TaskDialog

convert = Convert()
model = Model()

doc = model.doc
# detect_walls_from_lines()
# create_walls_where_detected()

wall_width = .15

def is_vertical(line):
    if type(line) is db.ModelLine:
        startpoint_x = round(line.GeometryCurve.GetEndPoint(0).X, 3)
        endpoint_x = round(line.GeometryCurve.GetEndPoint(1).X, 3)
        return startpoint_x == endpoint_x
    else:
        pass

def is_horizontal(line):
    startpoint_y = round(line.GeometryCurve.GetEndPoint(0).Y, 3)
    endpoint_y = round(line.GeometryCurve.GetEndPoint(1).Y, 3)
    
    return startpoint_y == endpoint_y

def is_diagonal(line):
    return not(is_vertical(line) or is_horizontal(line))
vertical_lines = [line for line in model.lines if is_vertical(line)]
horizontais = [line for line in model.lines if is_horizontal(line)]
diagonais = [line for line in model.lines if is_diagonal(line)]
dist_minima_em_cm_entre_duas_linhas_paralelas = .4

def get_distance_between_lines(lineA, lineB, ref_direction="horizontal"):
    if ref_direction == "horizontal":
        startpoint_y_lineA = lineA.GeometryCurve.GetEndPoint(0).Y
        startpoint_y_lineB = lineB.GeometryCurve.GetEndPoint(0).Y
        distance = startpoint_y_lineA - startpoint_y_lineB
    if ref_direction == "vertical":
        startpoint_x_lineA = lineA.GeometryCurve.GetEndPoint(0).X
        startpoint_x_lineB = lineB.GeometryCurve.GetEndPoint(0).X
        # print(startpoint_x_lineA, startpoint_x_lineB)
        distance = startpoint_x_lineA - startpoint_x_lineB
    else:
        pass
    return abs(distance)

def distance_between_lines_is_acceptable(distance_between_lines):
    return convert.ft_to_m(distance_between_lines) <= dist_minima_em_cm_entre_duas_linhas_paralelas

def get_longest_line(lineA, lineB):
    return lineA if lineA.GeometryCurve.Length >= lineB.GeometryCurve.Length else lineB
    
def get_shortest_line(lineA, lineB):
    return lineA if lineA.GeometryCurve.Length < lineB.GeometryCurve.Length else lineB

activeLevel = doc.ActiveView.GenLevel
def create_walltype_whith_one_layer_and_given_thickness(thickness_in_meters):    
    basic_walltypes = [wt for wt in model.walltypes if str(wt.Kind) == "Basic"]
    generic_walltype = basic_walltypes[0]
        
    t = db.Transaction(doc, "Create Wall Type with {}cm thickness".format(int(thickness_in_meters*100)))
    
    t.Start()
    new_walltype = generic_walltype.Duplicate("Gen {}{}".format(round(int(thickness_in_meters*100)), "cm"))
    print(new_walltype, generic_walltype)
    compound_structure = generic_walltype.GetCompoundStructure()
    print(new_walltype, "(new wall type)", compound_structure, "(compound structure)")
    layer = compound_structure.GetLayers()[0]
    layer.Width = convert.m_to_ft(thickness_in_meters)
    compound_structure.SetLayers([layer])
    db.WallType.SetCompoundStructure(new_walltype, compound_structure)
    t.Commit()
    
    return new_walltype
    

wt = create_walltype_whith_one_layer_and_given_thickness(.4)

def get_existing_walls():
    return db.FilteredElementCollector(doc).OfCategory(
        db.BuiltInCategory.OST_Walls
    ).WhereElementIsNotElementType().ToElements()

def wall_exists_at_location(curve, tolerance=0.1):
    """Verifica se já existe uma parede sobre (ou muito próxima de) a curva informada."""
    new_start = curve.GetEndPoint(0)
    new_end = curve.GetEndPoint(1)
    new_mid = curve.Evaluate(0.5, True)

    for wall in get_existing_walls():
        loc = wall.Location
        if not isinstance(loc, db.LocationCurve):
            continue
        ex_curve = loc.Curve
        ex_start = ex_curve.GetEndPoint(0)
        ex_end = ex_curve.GetEndPoint(1)
        ex_mid = ex_curve.Evaluate(0.5, True)

        if new_mid.DistanceTo(ex_mid) > tolerance:
            continue

        endpoints_match = (
            (new_start.DistanceTo(ex_start) < tolerance and new_end.DistanceTo(ex_end) < tolerance)
            or (new_start.DistanceTo(ex_end) < tolerance and new_end.DistanceTo(ex_start) < tolerance)
        )
        if endpoints_match:
            return True
    return False

def create_wall(startpoint, endpoint, wall_type=wt):
    curve = db.Line.CreateBound(startpoint, endpoint)

    if wall_exists_at_location(curve):
        print("Parede ja existe nesta localizacao, pulando criacao. (curva: {} -> {})".format(startpoint, endpoint))
        return None

    altura = convert.m_to_ft(2)
    offset = 0
    flip = False
    struct = False

    wall = db.Wall.Create(
        doc,
        curve,
        wall_type.Id,
        activeLevel.Id,
        altura,
        offset,
        flip,
        struct
    )
    wall_location_line = wall.get_Parameter(db.BuiltInParameter.WALL_KEY_REF_PARAM)
    wall_location_line.Set(1)
    return wall

vertical_pairs = []

def lines_represent_a_wall(distance_between_lines):
    return distance_between_lines_is_acceptable(distance_between_lines)

# if vertical_lines:
#     i = 0

#     while i < len(vertical_lines):
#         first = vertical_lines[i]

#         found_pair = False
#         j = i + 1


#         while j < len(vertical_lines) and not found_pair:
#             next_up = vertical_lines[j]
#             dist = get_distance_between_lines(first, next_up, "vertical")
            
#             try:
#                 t = db.Transaction(doc, "Create Wall element")
#                 t.Start()        
#                 new_walltype = db.WallType.Duplicate(wt, "generica_{}{}".format(dist, "cm"))
#                 db.WallType.SetCompoundStructure(new_walltype, wt.GetCompoundStructure())
#                 t.Commit()
#             except Revit.Exceptions.ArgumentException as e:
#                 print("WallType with name generica_{}{} already exists.".format(dist, "cm"))
#                 t.RollBack()

#             # print("comparando {} com {}".format(first.Id, next_up.Id))
#             inicio_linha_1 = first.GeometryCurve.GetEndPoint(0).Y
#             inicio_linha_2 = next_up.GeometryCurve.GetEndPoint(0).Y
#             fim_linha_1 = first.GeometryCurve.GetEndPoint(1).Y
#             fim_linha_2 = next_up.GeometryCurve.GetEndPoint(1).Y
#     # ao menos um ponto (seja a extrmeiudad einicial ou a final da linha) deve estra contido no intervalo
#     # ocupado pela outra linha (intevraloe ocupado = qyualquer valor float entre suas duas extremidades)
#     # sejam elas positivas ou negativas  ou uma positiva e a outra negativa.
#     #e essas extremidades estao na direcao perpendicular a direcao da linha. por emeploi 
#     # se se trata de uma linh vertical, o eixo horizontal é o X, e sera a referencia pra esse vaso.
#             condicao_1 = inicio_linha_1 < fim_linha_2 and fim_linha_1           
#             # adaptar abaixo:
#             # def share_point_in_perpendicular_axis(line_A, line_B):
# #     # for two given lines, checks if they share a common point in the opposite axis
# #     # to that in which they're located as straight horizontal (x) ou vertical (y) lines.
# #     # This means they probably represent two faces of a same wall, if wall_thickness 
# #     # condition is also true.
# #     if is_horizontal(line_A) and is_horizontal(line_B):
# #         if (
# #             line_B.start_x <= line_A.start_x <= line_B.end_x
# #         ) or (
# #             line_A.start_x <= line_B.start_x <= line_A.end_x
# #         ) or (
# #             line_B.end_x <= line_A.end_x <= line_B.start_x
# #         ) or (
# #             line_A.end_x <= line_B.end_x <= line_A.start_x
# #         ):
# #             return True
# #     elif is_vertical(line_A) and is_vertical(line_B):
# #         if (
# #             line_B.start_y >= line_A.start_y >= line_B.end_y
# #         ) or (
# #             line_A.start_y >= line_B.start_y >= line_A.end_y
# #         ) or (
# #             line_B.end_y >= line_A.end_y >= line_B.start_y
# #         ) or (
# #             line_A.end_y >= line_B.end_y >= line_A.start_y
# #         ):
# #             return True
# #     elif is_diagonal(line_A) and is_diagonal(line_B):
# #         return True
# #     return False
#             if lines_represent_a_wall(dist):
#                 dislocation = dist / 2
#                 vertical_pairs.append((first, next_up))
#                 # print("par encontrado:", first.Id, next_up.Id)
#                 vertical_lines.pop(j)
#                 vertical_lines.pop(i)
#                 found_pair = True
#             else:
#                 j += 1
#         if not found_pair:
#             i += 1

# class ModelLine:
#     # def __init__(self, RevitOBJ: ModelLines):
#     def __init__(self, RevitOBJ):
#         self.startpoint = RevitOBJ.GeometryCurve.GetEndPoint(0)
#         self.endpoint = RevitOBJ.GeometryCurve.GetEndPoint(1)
#         self.style = RevitOBJ.LineStyle.Name
#         self.length = RevitOBJ.GeometryCurve.Length
#         self.sketch_plane = RevitOBJ.SketchPlane.Name
#         self.Id = RevitOBJ.Id
       
#     @property
#     def start_x(self):
#         return round(self.startpoint.X, 5)
    
#     @property
#     def start_y(self):
#         return round(self.startpoint.Y, 5)
    
#     @property
#     def start_z(self):
#         return round(self.startpoint.Z, 5)

#     @property
#     def end_x(self):
#         return round(self.endpoint.X, 5)

#     @property
#     def end_y(self):
#         return round(self.endpoint.Y, 5)
    
#     @property
#     def end_z(self):
#         return round(self.endpoint.Z, 5)
    
#     def relative_position(ref_line, other_line):
#         # this for now only covers cases where both lines have positive values for their start points and which direction is vertical
#         # cases:  linhas verticais,  quadrante positivo, negativo ou misto.
#         # linhas horizontais, quadrante positivo, negativo ou misto.
#         if ref_line.start_x < other_line.start_x:
#             return "left"
#         elif ref_line.start_x > other_line.start_x:
#             return "right"
#         else:
#             return "theyre both vertical in direction and equal in X axis positioning"

# for a,b in vertical_pairs:
#     longest = ModelLine(get_longest_line(a,b))
#     shortest = ModelLine(get_shortest_line(a,b))
#     print(longest.start_x, shortest.start_x)
#     # this actually depends on the direction of the lines involved.
#     start_dislocated_negatively = db.XYZ(
#         longest.start_x - dislocation, 
#         longest.start_y, 
#         longest.start_z
#         )
#     start_dislocated_positively = db.XYZ(
#         longest.start_x + dislocation,
#         longest.start_y, 
#         longest.start_z
#         )
#     end_dislocated_negatively = db.XYZ(
#         longest.end_x - dislocation, 
#         longest.end_y, 
#         longest.end_z
#         )
#     end_dislocated_positively = db.XYZ(
#         longest.end_x + dislocation,
#         longest.end_y, 

#         longest.end_z
#         )
#     t = db.Transaction(doc, "Create Wall element")
#     t.Start()        
#     # detectar primeiro se ja existe instancia de parede ocupando qualquer pnto da parede q se deseja criar,
#     # para evitar conflito e annoying Revit warning.
#     if ModelLine.relative_position(longest, shortest) == "right":
#         create_wall(start_dislocated_negatively, end_dislocated_negatively)
#     elif ModelLine.relative_position(longest, shortest) == "left":
#         create_wall(start_dislocated_positively, end_dislocated_positively)
#     t.Commit()

# import math
# import unicodedata
# def get_name(element):
#     if element is not None:
#         model_type_param = element.get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_NAME)
#         room_name_param = element.get_Parameter(DB.BuiltInParameter.ROOM_NAME)
        
#         # Obtenha o valor do parâmetro somente se ele não for None
#         model_type_name = model_type_param.AsString() if model_type_param else None
#         room_name = room_name_param.AsString() if room_name_param else None

#         # Prioriza o nome do tipo de modelo
#         if model_type_name is not None:
#             name = model_type_name
#         elif room_name is not None:
#             name = room_name
#         else:
#             name = "Sem nome"  # Nome padrão caso nenhum parâmetro exista
        
#         # Remove acentos e caracteres especiais, depois capitaliza
#         return capitalize_string(remove_acentos(name))
    
#     return "Elemento inválido"
    
# def get_names(RevitListOfElements):
#     elem_names_list = [get_name(element) for element in RevitListOfElements]
#     return elem_names_list

# class ModelLine:
#     # def __init__(self, RevitOBJ: ModelLines):
#     def __init__(self, RevitOBJ):
#         self.startpoint = RevitOBJ.GeometryCurve.GetEndPoint(0)
#         self.end_point = RevitOBJ.GeometryCurve.GetEndPoint(1)
#         self.style = RevitOBJ.LineStyle.Name
#         self.length = RevitOBJ.GeometryCurve.Length
#         self.sketch_plane = RevitOBJ.SketchPlane.Name
       
#     @property
#     def start_x(self):
#         return round(self.startpoint.X, 5)
    
#     @property
#     def start_y(self):
#         return round(self.startpoint.Y, 5)
    
#     @property
#     def start_z(self):
#         return round(self.startpoint.Z, 5)

#     @property
#     def end_x(self):
#         return round(self.end_point.X, 5)

#     @property
#     def end_y(self):
#         return round(self.end_point.Y, 5)
    
#     @property
#     def end_z(self):
#         return round(self.end_point.Z, 5)

# def find_id_by_element_name(RevitListOfElements, keyword):
#     for element in RevitListOfElements:
#         if get_name(element).lower() == keyword:
#             return element.Id
# default_walltype_id = find_id_by_element_name(interface.walltypes, "Generica 15cm")


# def normalize_string(input_string):
#     return unicodedata.normalize('NFKD', input_string).encode('ASCII', 'ignore').decode('ASCII')

# doc = __revit__.ActiveUIDocument.Document

# # find groups of lines that represent the faces of a same wall and store them
# default_wall_width = convert_m_to_ft(0.15)

# def default_wall_widths(list_of_common_wall_widths):
#     return [convert_m_to_ft(common_w) for common_w in list_of_common_wall_widths]

# print(default_wall_widths([0.15, 0.20, 0.25, 0.30]))
# # print(default_wall_width)
# print(default_walltype_id)  # Deve retornar um número válido (ID do tipo de parede)

# cad_wall_lines = interface.filter_lines_by_name(["Parede"])
# tolerance = default_wall_width * 0.05 #allows +/- 2% variation to account for minor CAD drawing imprecisions

# def is_horizontal(model_line):
#     return abs(model_line.end_y - model_line.start_y) == 0

# def is_vertical(model_line):
#     return abs(model_line.end_x - model_line.start_x) == 0

# def is_diagonal(model_line):
#     return model_line.end_x - model_line.start_x != 0 and model_line.end_y - model_line.start_y != 0

# def offset_equals_wall_width(line_A, line_B):
#     def dist_between_lines():
#         if is_horizontal(line_B) and is_horizontal(line_A):
#             return abs(line_B.start_y - line_A.start_y)
#         elif is_vertical(line_B) and is_vertical(line_A):
#             return abs(line_B.start_x - line_A.start_x)
#         # elif is_diagonal(line_A) and is_diagonal(line_B):
            
#         else:
#             return default_wall_width
#     offset = dist_between_lines()
#     # print(abs(offset - default_wall_width))
#     if abs(offset - default_wall_width) < tolerance:
#         return True
#     else:
#         return False

# def are_parallel(line_A, line_B):
#     #two given lines must share the same plane (level elevation) and be equidistant at any point
#     start_A = line_A.startpoint
#     end_A = line_A.end_point
#     start_B = line_B.startpoint
#     end_B = line_B.end_point

#     lines_share_same_plane = abs(start_A.Z - start_B.Z) < 1e-6
   
#     # Calcula os vetores diretores
#     vector_A = end_A - start_A
#     vector_B = end_B - start_B
    
#     cross_product = vector_A.CrossProduct(vector_B)
#     # Verifica se o comprimento do vetor cruzado é quase zero (linhas perfeitamente paralelas)
#     if cross_product.IsZeroLength():
#         is_parallel = True
#     else:
#         # Para diagonais ou imprecisões, verifica se o comprimento do produto vetorial é pequeno (< 1)
#         is_parallel = cross_product.GetLength() < .4
#     # Retorna verdadeiro se as linhas estiverem no mesmo plano e forem paralelas
#     return lines_share_same_plane and is_parallel

# def share_point_in_perpendicular_axis(line_A, line_B):
#     # for two given lines, checks if they share a common point in the opposite axis
#     # to that in which they're located as straight horizontal (x) ou vertical (y) lines.
#     # This means they probably represent two faces of a same wall, if wall_thickness 
#     # condition is also true.
#     if is_horizontal(line_A) and is_horizontal(line_B):
#         if (
#             line_B.start_x <= line_A.start_x <= line_B.end_x
#         ) or (
#             line_A.start_x <= line_B.start_x <= line_A.end_x
#         ) or (
#             line_B.end_x <= line_A.end_x <= line_B.start_x
#         ) or (
#             line_A.end_x <= line_B.end_x <= line_A.start_x
#         ):
#             return True
#     elif is_vertical(line_A) and is_vertical(line_B):
#         if (
#             line_B.start_y >= line_A.start_y >= line_B.end_y
#         ) or (
#             line_A.start_y >= line_B.start_y >= line_A.end_y
#         ) or (
#             line_B.end_y >= line_A.end_y >= line_B.start_y
#         ) or (
#             line_A.end_y >= line_B.end_y >= line_A.start_y
#         ):
#             return True
#     elif is_diagonal(line_A) and is_diagonal(line_B):
#         return True
#     return False

# grouped_lines = []

# i = 0
# for l in interface.levels:
#     print(l.Id)

# for i in range(len(cad_wall_lines)):
#     def lines_have_minimum_length(line_A, line_B):
#         min_length = default_wall_width*2.5
#         def line_length(line):
#             return line.get_Parameter(DB.BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble()
#         # print(line_length(line_A), line_length(line_B))
#         return line_length(line_A) >= min_length and line_length(line_B) >= min_length
    
#     ref_line = ModelLine(cad_wall_lines[i])
#     lines_of_same_wall = [ref_line]
#     # def line_level_id(line):
#     #     line_sketch_plane = line.get_Parameter(DB.BuiltInParameter.SKETCH_PLANE_PARAM).AsString()
#     #     linel_level_name = line_sketch_plane.split()[-1]
#     #     linel_level_name = normalize_string(linel_level_name)  # Normaliza a string para remover acentos

#     #     for level in interface.levels:
#     #         print((normalize_string(level.Name) == linel_level_name)
#     #         line_level_id = level.Id if linel_level_name == normalize_string(level.Name) else None
#     #     print(linel_level_name, line_level_id)
#     #     return line_level_id

#     # line_level_id(cad_wall_lines[i])

#     n = i+1
#     while n < len(cad_wall_lines):
#         next_line = ModelLine(cad_wall_lines[n])
#         # print('comparing now {} to {}:'.format(str(cad_wall_lines[i].Id), str(cad_wall_lines[n].Id)))
#         # print('have intersecting points?', share_point_in_perpendicular_axis(ref_line, next_line))
#         # print('offset equals width?', offset_equals_wall_width(ref_line, next_line))
#         # print('parallel?', are_parallel(ref_line, next_line))
#         # print(lines_have_minimum_length(cad_wall_lines[i], cad_wall_lines[n]))
#         if (
#             are_parallel(ref_line, next_line)
#             and offset_equals_wall_width(ref_line, next_line)
#             and share_point_in_perpendicular_axis(ref_line, next_line)
#             and lines_have_minimum_length(cad_wall_lines[i], cad_wall_lines[n])
#         ):
#             lines_of_same_wall.append(next_line)
#         n+=1

#     if len(lines_of_same_wall) > 1:
#         grouped_lines.append(lines_of_same_wall)
#     i+=1

# # print(grouped_lines)
# def create_wall(doc, bound_line, default_wall_type_id, level_id, misterious_param_1 = 10, misterious_param_2 = 1, flag_1 = False, flag_2 = False):
#     t = DB.Transaction(doc, "Create new wall instance from cad line")
#     t.Start()
#     try:
#         wall = DB.Wall.Create(doc, bound_line, default_wall_type_id, level_id, 10, 0, False, False)
#         wall_location_line = wall.get_Parameter(DB.BuiltInParameter.WALL_KEY_REF_PARAM)
#         if wall_location_line and wall_location_line.IsReadOnly == False:
#             wall_location_line.Set(0) < # Define Linha central da parede como Linha de localizacao
#     except Exception as e:
#         print("Error creating wall instance: {}".format(e))
#         pass
#     t.Commit()

# # print(grouped_lines)

# def longest(line_list):
#     if line_list[0].length > lines[1].length:
#         longest = line_list[0]
#     else:
#         longest = line_list[1]
#     return longest

# def equal_length(line_list):
#     if (line_list[0].length - lines[1].length) < tolerance:
#         return line_list[0]
#     else:
#         return line_list[1]

# for lines in grouped_lines:
#     # Ordena as linhas do grupo pelo menor ponto inicial (start_x, start_y)
#     sorted_lines = sorted(
#         lines,
#         key=lambda line: (line.start_x, line.start_y)
#     )
#     # print(sorted_lines)
#     # Seleciona a primeira como linha de referência e a segunda como linha auxiliar
#     ref_line = sorted_lines[0]
#     aux_line = sorted_lines[1]
#     # print(ref_line.start_x, aux_line.start_x)
#     # Vetores direção para linha de referência
#     ref_dir = DB.XYZ(ref_line.end_x - ref_line.start_x, ref_line.end_y - ref_line.start_y, 0)
    
#     # Determina deslocamento para criar a linha entre as duas
#     offset_x = default_wall_width / 2 if abs(ref_dir.X) < abs(ref_dir.Y) else 0
#     offset_y = default_wall_width / 2 if abs(ref_dir.Y) < abs(ref_dir.X) else 0

#     # Ajusta deslocamento com base na posição relativa
#     if aux_line.start_x > ref_line.start_x:  # Auxiliar à direita
#         offset_x *= -1
#     if aux_line.start_y > ref_line.start_y:  # Auxiliar acima
#         offset_y *= -1

#     # Cria os novos pontos deslocados
#     a = ref_line.startpoint - DB.XYZ(offset_x, offset_y, 0)
#     b = ref_line.end_point - DB.XYZ(offset_x, offset_y, 0)
    
#     # Tenta criar a nova parede
#     try:
#         bound_line = DB.Line.CreateBound(a, b)
#         create_wall(doc, bound_line, default_walltype_id, interface.levels[0].Id, 10, 0, False, False)
#     except NameError as e:
#         print("Erro ao criar parede: {}".format(e))