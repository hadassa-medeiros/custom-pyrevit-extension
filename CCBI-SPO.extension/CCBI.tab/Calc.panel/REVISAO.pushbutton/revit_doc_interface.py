# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB

def map_cat_to_elements(self, keyword):
    return DB.FilteredElementCollector(self.doc).OfCategory(
        self.category_map[keyword]
    ).WhereElementIsNotElementType().ToElements()
    
class RevitDocInterface:
    def __init__(self, RevitDoc=__revit__.ActiveUIDocument.Document):
        self.doc = RevitDoc# self.collector = DB.FilteredElementCollector(RevitDoc)
        self.category_map = {
            # "all_elements": DB.Element
            "walls": DB.BuiltInCategory.OST_Walls,
            "floors": DB.BuiltInCategory.OST_Floors,
            "rooms": DB.BuiltInCategory.OST_Rooms,
            "ceilings": DB.BuiltInCategory.OST_Ceilings,
            "lines": DB.BuiltInCategory.OST_Lines,
            "levels": DB.BuiltInCategory.OST_Levels,
            "walltypes": DB.WallType,
            "curves": DB.CurveElement,
            "room_separation_lines": DB.CurveElementFilter(DB.CurveElementType.RoomSeparation),
            "materials": DB.BuiltInCategory.OST_Materials,
        }
    # def filter_elements_by_name(elements_list, reference_keywords):
    #     for element in elements_list:
    @property
    def rooms(self):
        return map_cat_to_elements(self, 'rooms')

    @property
    def floors(self):
        return map_cat_to_elements(self, 'floors')
    
    @property
    def ceilings(self):
        return map_cat_to_elements(self, 'ceilings')

    @property
    def levels(self):
        return list(map_cat_to_elements(self, 'levels'))
    
    @property
    def materials(self):
        return DB.FilteredElementCollector(self.doc).OfCategory(
            self.category_map["materials"]
        ).WhereElementIsNotElementType().ToElements()
    
    @property
    def walltypes(self):
        return DB.FilteredElementCollector(self.doc).OfClass(
            self.category_map["walltypes"]
        ).ToElements()
    
    @property
    def walls(self):
        return DB.FilteredElementCollector(self.doc).OfClass(
            self.category_map["walls"]
        ).WhereElementIsNotElementType().ToElements()

    @property
    def lines(self):
        return DB.FilteredElementCollector(self.doc).OfCategory(
            self.category_map["lines"]
        ).ToElements()
            
    @property
    def curves(self):
        return DB.FilteredElementCollector(self.doc).OfClass(
            self.category_map["curves"]
        ).ToElements()
    
    @property
    def model_lines(self):
        filter = DB.CurveElementFilter(DB.CurveElementType.ModelCurve)
        return DB.FilteredElementCollector(self.doc).WherePasses(filter).WhereElementIsNotElementType().ToElements()
        
    # def filter_elements_by_name(self, elements_list, reference_keywords):
    #     filter = [DB.FilterStringContains(DB.BuiltInParameter.ALL_MODEL_TYPE_NAME, keyword) for keyword in reference_keywords]
    #     filtered_elements = [element for element in elements_list if DB.FilteredElementCollector(self.doc).WherePasses(filter).ToElements()]
    #     return filtered_elements
    def filter_elements_by_name(self, elements_list, reference_keywords):
        filtered_elements = [element for element in elements_list if any(name in get_name(element) for name in reference_keywords)]
        return filtered_elements
    
    def filter_lines_by_name(self, reference_keywords):
        reference_keywords = [name.strip().upper() for name in reference_keywords]
        filtered_lines = [
            line for line in self.model_lines if any(name in line.LineStyle.Name.strip().upper() for name in reference_keywords)
            ]
        return filtered_lines
    
def find_id_by_element_name(RevitListOfElements, keyword):
    for element in RevitListOfElements:
        if get_name(element) == keyword:
            return element.Id

def get_ids_of(RevitListOfElements):
    elem_ids_list = [element.Id for element in RevitListOfElements]
    return elem_ids_list

def get_name(element):
    if element is not None:
        model_type_param = element.get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_NAME)
        room_name_param = element.get_Parameter(DB.BuiltInParameter.ROOM_NAME)
        
        # Obtenha o valor do parâmetro somente se ele não for None
        model_type_name = model_type_param.AsString() if model_type_param else None
        room_name = room_name_param.AsString() if room_name_param else None

        if model_type_name is not None:
            return model_type_name
        elif room_name is not None:
            return room_name
        else:
            return "Sem nome"  # Nome padrão caso nenhum parâmetro exista
    return "Elemento inválido"
    
def get_names(RevitListOfElements):
    elem_names_list = [get_name(element) for element in RevitListOfElements]
    return elem_names_list

def get_element(RevitListOfElements):
    elements_list = [element for element in RevitListOfElements]
    return elements_list[0]

def meter_to_double(value_in_meters):
    meter_to_double_factor = 3.280840
    value_in_double = round(value_in_meters * meter_to_double_factor, 5)
    return value_in_double

def double_to_square_meter(value_in_double):
    meter_to_double_factor = 3.280840
    value_in_double = round(value_in_meters * meter_to_double_factor, 5)
    return value_in_double

def get_room_number(roomElement):
    return roomElement.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString()

class ModelLine:
    # def __init__(self, RevitOBJ: ModelLines):
    def __init__(self, RevitOBJ):
        self.start_point = RevitOBJ.GeometryCurve.GetEndPoint(0)
        self.end_point = RevitOBJ.GeometryCurve.GetEndPoint(1)
        self.style = RevitOBJ.LineStyle.Name
        self.length = RevitOBJ.GeometryCurve.Length
        self.sketch_plane = RevitOBJ.SketchPlane.Name
       
    @property
    def start_x(self):
        return round(self.start_point.X, 5)
    
    @property
    def start_y(self):
        return round(self.start_point.Y, 5)
    
    @property
    def start_z(self):
        return round(self.start_point.Z, 5)

    @property
    def end_x(self):
        return round(self.end_point.X, 5)

    @property
    def end_y(self):
        return round(self.end_point.Y, 5)
    
    @property
    def end_z(self):
        return round(self.end_point.Z, 5)
    
if __name__ == "__main__":
    interface = RevitDocInterface()
    print("Níveis: {}".format(interface.levels))
    # print("Tipos de parede: {interface.walltypes}")
    # print("Linhas: {interface.lines}")

# # this may have some utility:
# rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms)

# for r in rooms:
# 	area_amb = round(((r.Area*0.3048)/3.2808),2)
# 	nome = Element.Name.GetValue(r)
# 	print('{}-{}m'.format(nome, area_amb))
# 	nome_iniciais = nome[0:4]
# 	if nome_iniciais == 'SALA':
# 		print(nome + 'm²' + 'É SALA DE AULA')

# print(rooms)

# # Area from room tags:
# # Get the selected room
# selection = __revit__.ActiveUIDocument.Selection

# room = doc.GetElement(element_id)

# area_tags = list(room.GetDependentElements(Filters.AreaTagFilter(), False))
# if area_tags:
# 	area_value = area_tag.Area
# print("Room Area (from AreaTag):", area_value)

# # total wall areas:
# wall_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType()

# total_area = 0.0
# print(wall_collector)

# for wall in wall_collector:
#     area_param = wall.Parameter[BuiltInParameter.HOST_AREA_COMPUTED]
#     if area_param:
#         total_area = total_area + area_param.AsDouble()
# print("Total area of walls is {:.2f}".format(total_area))


# exemplo de FILTRO tipo ElementParameterFilter:
# param_value_provider = DB.ParameterValueProvider(elem_id)

# rule_evaluator = DB.FilterStringEquals()
# rule_str = 'PROJETO'

# f_rule = DB.FilterStringRule(param_value_provider, rule_evaluator, rule_str)

# filter = DB.ElementParameterFilter(f_rule, True)

# filtered_elements = all_walls.WherePasses(
#     filter
#     ).WhereElementIsNotElementType().ToElements()