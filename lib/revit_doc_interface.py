# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
import unicodedata
from pyrevit import forms, script

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
app = doc.Application


def get_elem_param(elem, builtin_or_shared_param):
    if isinstance(builtin_or_shared_param, DB.BuiltInParameter):
        elem_param = elem.get_Parameter(builtin_or_shared_param)
    else:
        elem_param = elem.LookupParameter(builtin_or_shared_param)
    return elem_param

def new_param_value(elem, param, correct_value):
    elem_param = get_elem_param(elem, param)
    param_value = elem_param.Id
    # print(param_value)

    if type(param_value) == type(correct_value) and param_value != correct_value:
        t = DB.Transaction(doc, "Correct created phase parameter")
        t.Start()
        try:
            elem_param.Set(correct_value)
            print(
                "{} corrigido (era {})"
                .format(elem.Name, param_value)
                )
        except Exception as e:
            print(e)
            pass
        t.Commit()
    else:
        print(
              'Os argumentos deveriam ter o mesmo tipo, mas sao {} e {}'.format(
                   type(param_value), type(correct_value)
              )
        )   

def normalize_param(param_obj):
    return param_obj.AsString() if param_obj and param_obj.HasValue else None

def get_project_parameter(doc, param_name_or_obj, param_is_builtin = bool):
    project_info_elem = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_ProjectInformation).FirstElement()

    try:
        if param_is_builtin:
            param_obj = param_name_or_obj
            return project_info_elem.get_Parameter(param_obj).AsValueString()
        else:
            param_name = param_name_or_obj
            return project_info_elem.LookupParameter(param_name).AsValueString()
    except AttributeError:
        print('O parametro informado nao foi encontrado no modelo')
        
# open shared parameters file if existent
def open_shared_params_file():
    sp_file = app.OpenSharedParameterFile()

    if not sp_file:
        forms.alert('Shared parameters file was not found, add it and try again.')

    dict_shared_params = {}
    for group in sp_file.Groups:
        for p_def in group.Definitions:
            combined_name = '{}_{}'.format(group.Name, p_def.Name)
            dict_shared_params[combined_name] = p_def
    return dict_shared_params

# def find_range(csv_table):
    # for row in csv_table:
        # if 'CÓDIGO' in row:
        # start_row = row[]
        # start_column 
    # print(csv_table[start_row][start_column])

# pick csv trough pyRevit forms 
# (to be used in pushbutton to compare data from table to data from model)
def pick_csv_file():
    return forms.pick_file(file_ext='csv', multi_file=False)

def save_to_csv(list_with_data, csv_file_path):
  csv_rows = list_with_data
  file = script.dump_csv(csv_rows, csv_file_path)
  # os.open(file)
  # output_path = os.path.join(
  # os.path.expanduser('~'), 
  # 'Areas_rev_ambientes{}.csv'
  # .format(doc.Title)
  #)
  # script.load_csv("C:\Users\Administrator\Downloads\CCEN Administração - Planilha Áreas.xlsx - GERAL.csv")
  script.load_csv(csv_file_path)

def remove_acentos(texto):
    # Normaliza o texto e remove os acentos
    nfkd_form = unicodedata.normalize('NFKD', texto)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def capitalize_string(texto):
    # Capitaliza cada palavra da string
    return texto.strip().title()

def get_selected_elements(uidoc):
    return [uidoc.Document.GetElement(elem_id) for elem_id in uidoc.Selection.GetElementIds()] 

def map_cat_to_elements(self, keyword):
    return DB.FilteredElementCollector(self.doc).OfCategory(
        self.category_map[keyword]
    ).WhereElementIsNotElementType().ToElements()

def map_cat_to_element_types(self, keyword):
    return DB.FilteredElementCollector(self.doc).OfCategory(
        self.category_map[keyword]
    ).WhereElementIsElementType().ToElements()

class RevitDocInterface:
    def __init__(self, RevitDoc=doc):
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
            "structural_columns": DB.BuiltInCategory.OST_StructuralColumns,
            "structural_framing": DB.BuiltInCategory.OST_StructuralFraming,
            "columns": DB.BuiltInCategory.OST_Columns,
            "windows": DB.BuiltInCategory.OST_Windows,
            "doors": DB.BuiltInCategory.OST_Doors,

        }
    # def filter_elements_by_name(elements_list, reference_keywords):
    #     for element in elements_list:
    @property
    def window_types(self):
        return map_cat_to_element_types(self, 'windows')
    
    @property
    def windows(self):
        return map_cat_to_elements(self, 'windows')
    
    @property
    def doors(self):
        return map_cat_to_elements(self, 'doors')
    
    @property
    def columns(self):
        return map_cat_to_elements(self, 'columns')

    @property
    def beams(self):
        return map_cat_to_elements(self, 'structural_framing')

    @property
    def struct_columns(self):
        return map_cat_to_elements(self, 'structural_columns')

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
        return DB.FilteredElementCollector(self.doc).OfCategory(
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
    
    def find_phase_by_name(self, phase_name):
        for phase in self.doc.Phases:
            if phase.Name == phase_name.upper():
                return phase
        return None
    
def find_id_by_element_name(RevitListOfElements, keyword):
    for element in RevitListOfElements:
        if get_name(element).lower() == keyword:
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

        # Prioriza o nome do tipo de modelo
        if model_type_name is not None:
            name = model_type_name
        elif room_name is not None:
            name = room_name
        else:
            name = "Sem nome"  # Nome padrão caso nenhum parâmetro exista
        
        # Remove acentos e caracteres especiais, depois capitaliza
        return capitalize_string(remove_acentos(name))
    
    return "Elemento inválido"
    
def get_names(RevitListOfElements):
    elem_names_list = [get_name(element) for element in RevitListOfElements]
    return elem_names_list

def get_element(RevitListOfElements):
    elements_list = [element for element in RevitListOfElements]
    return elements_list[0]

def metric_to_double(value_in_meters):
    meter_to_double_factor = 3.280840
    value_in_double = round(value_in_meters * meter_to_double_factor, 5)
    return value_in_double

def double_to_metric(value):
    meter_to_double_factor = 3.280840
    value_in_metric = value/meter_to_double_factor
    return round(value_in_metric, 2)

def get_room_number(roomElement):
    return roomElement.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString()

def sq_ft_to_m2(area_double):
    """Converte valor interno do Revit (pés², double) para área em metros quadrados."""
    return round(area_double * 0.092903, 4)

def get_elem_from_typeId(elem):
    return doc.GetElement(elem.GetTypeId()) if elem.GetTypeId() else None

def get_room_area(room_elem):
    if isinstance(room_elem, DB.SpatialElement) and room_elem.Category.Id.IntegerValue == int(DB.BuiltInCategory.OST_Rooms):
        return room_elem.get_Parameter(DB.BuiltInParameter.ROOM_AREA).AsDouble()
    
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