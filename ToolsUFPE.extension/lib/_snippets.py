# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB 
from _base import *

""" 
def normalize(str):

"""

""" 
def convert_unit(input):

"""

def set_value(elem, param_name_or_enum, new_value, transaction_name):
    param = elem.LookupParameter(param_name_or_enum) if isinstance(param_name_or_enum, str) else elem.get_Parameter(param_name_or_enum)

    if not param:
        print("❌ Parâmetro '{}' não encontrado no elemento.".format(param_name_or_enum))
        return

    if param.IsReadOnly:
        print("⚠️ Parâmetro '{}' é somente leitura.".format(param.Definition.Name))
        return

    try:
        # Inicia a transação
        t = DB.Transaction(doc, transaction_name)
        t.Start()

        # Tenta definir o valor
        if not param.Set(new_value):
            print("⚠️ Não foi possível definir o valor de '{}'.".format(param.Definition.Name))
        
        t.Commit()
        print("✅ Parâmetro '{param.Definition.Name}' atualizado com sucesso para {new_value}.")

    except Exception as e:
        print("❌ Erro ao tentar definir o parâmetro '{}': {}".format(param_name_or_enum, e))
        if t.HasStarted() and not t.HasEnded():
            t.RollBack()
    finally:
        if t.HasStarted() and not t.HasEnded():
            t.Commit()

def get_selected():
    return [doc.GetElement(elem_id) for elem_id in uidoc.Selection.GetElementIds()]

def get_name(elem):
    if elem is not None:
        model_type_param = elem.get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_NAME)
        room_name_param = elem.get_Parameter(DB.BuiltInParameter.ROOM_NAME)
        
        model_type_name = model_type_param.AsString() if model_type_param else None
        room_name = room_name_param.AsString() if room_name_param else None

        if room_name:
            return room_name
        # if elem.Name:
        #     return elem.Name
        if model_type_name:
            return model_type_name
        else:
            return "S/N"
        # return capitalize_string(normalize(name))
    return "Invalid element"

def get_type_name(elem):
    if isinstance(elem, DB.Element):
        type_id = elem.GetTypeId()
        elem_type = doc.GetElement(type_id)
        elem_type_name = get_name(elem_type)
        return elem_type_name

    print(elem_type.Name)

class ElementCollections:
    def __init__(self):
        self.doc = doc
        self.category_map = {
            "walls": DB.BuiltInCategory.OST_Walls,
            "walltypes": DB.WallType,
            "floors": DB.BuiltInCategory.OST_Floors,
            "rooms": DB.BuiltInCategory.OST_Rooms,
            "ceilings": DB.BuiltInCategory.OST_Ceilings,
            "lines": DB.BuiltInCategory.OST_Lines,
            "levels": DB.BuiltInCategory.OST_Levels,
            "curves": DB.CurveElement,
            "room_separation_lines": DB.CurveElementFilter(DB.CurveElementType.RoomSeparation),
            "materials": DB.BuiltInCategory.OST_Materials,
            "structural_columns": DB.BuiltInCategory.OST_StructuralColumns,
            "structural_framing": DB.BuiltInCategory.OST_StructuralFraming,
            "columns": DB.BuiltInCategory.OST_Columns,
            "windows": DB.BuiltInCategory.OST_Windows,
            "doors": DB.BuiltInCategory.OST_Doors
        }

    
    def map_cat_to_elements(self, keyword):
        cat = self.category_map.get(keyword)
        if isinstance(cat, DB.ElementFilter):
            return DB.FilteredElementCollector(self.doc).WherePasses(cat).WhereElementIsNotElementType().ToElements()
        elif isinstance(cat, DB.BuiltInCategory):
            return DB.FilteredElementCollector(self.doc).OfCategory(cat).WhereElementIsNotElementType().ToElements()
        elif issubclass(cat, DB.Element):
            return DB.FilteredElementCollector(self.doc).OfClass(cat).WhereElementIsNotElementType().ToElements()
        else:
            return []
        
    def get_types(self, keyword):
        cat = self.category_map.get(keyword)
        return DB.FilteredElementCollector(self.doc).OfCategory(cat).WhereElementIsElementType()
    
    def __getattr__(self, name):
        if name in self.category_map:
            return self.map_cat_to_elements(name)
        raise AttributeError('Collection object has no attribute {}'.format(name))
    
class ModelLine:
    def __init__(self, line):
        self.start_point = line.GeometryCurve.GetEndPoint(0)
        self.end_point = line.GeometryCurve.GetEndPoint(1)
        self.style = line.LineStyle.Name
        self.length = line.GeometryCurve.Length
        self.sketch_plane = line.SketchPlane.Name

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
    