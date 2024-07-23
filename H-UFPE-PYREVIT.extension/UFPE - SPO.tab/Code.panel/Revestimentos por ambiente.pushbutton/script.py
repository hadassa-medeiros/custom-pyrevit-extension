# -*- coding: utf-8 -*-
import clr

clr.AddReference('RevitAPI')
# import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, BuiltInParameter, ElementCategoryFilter, LogicalOrFilter, HostObjAttributes, ElementId, Outline, BoundingBoxIntersectsFilter, Transaction

import Autodesk.Revit.UI.Selection as sel
from pyrevit import forms
# from rpw import revit, db, ui, forms

__title__     = "Revestimentos por ambiente"
__author__    = "Hadassa Medeiros"
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

# Importar bibliotecas necessárias

# Definir categorias relevantes
relevant_categories = [
    BuiltInCategory.OST_Ceilings, 
    BuiltInCategory.OST_Walls, 
    BuiltInCategory.OST_Floors
]

# Criar filtros de categoria e combinar com LogicalOrFilter
category_filters = [ElementCategoryFilter(cat) for cat in relevant_categories]
combined_filter = LogicalOrFilter(category_filters)

# Coletar elementos no documento ativo
doc = __revit__.ActiveUIDocument.Document
collector = FilteredElementCollector(doc).WherePasses(combined_filter)

# # Mostrar TODOS os elementos das categorias de interesse
# for elem in collector:
#     if elem is not None:
#         elem_type = doc.GetElement(elem.GetTypeId())
#         if elem_type is not None:
#             elem_category = elem.Category
#             elem_type_name = elem_type.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()

#             # Verificar condição
#             if 'REV' in elem_type_name or elem_category.Id.IntegerValue in [cat.value__ for cat in relevant_categories]:
#                 print("Elemento {} - Tipo: {} - Categoria: {}".format(elem.Id, elem_type, elem_type_name))

levels_collector =    FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels)
materials_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Materials)
floors_collector =     FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors)
ceilings_collector =    FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ceilings)
walls_collector =   FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls)
rooms_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms)

levels = list(levels_collector.WhereElementIsNotElementType().ToElements())
materials = materials_collector.ToElements()
rooms = list(rooms_collector.WhereElementIsNotElementType().ToElements())
floors = floors_collector.ToElements()
ceilings = ceilings_collector.ToElements()
walls = walls_collector.ToElements()
walls_instances = walls_collector.WhereElementIsNotElementType().ToElements()

ceilings_category = str(BuiltInCategory.OST_Ceilings)
walls_category = str(BuiltInCategory.OST_Walls)
floors_category = str(BuiltInCategory.OST_Floors)

relevant_categories = [ceilings_category, walls_category, floors_category]
wall_materials_ids_list = []
wall_materials_in_room = []
wall_mats = {}
info_per_room = {}
double_to_meter_divisor = 3.28084

rooms_total = 0 #Quantity of rooms analyzed.
room_numbers_and_names = ["{} - {}".format(
    room.get_Parameter(BuiltInParameter.ROOM_NUMBER).AsString(),
    room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()
) for room in rooms]

# Show a checkbox list for room selection

selected_rooms_and_names = forms.SelectFromList.show(room_numbers_and_names, button_name='Select Rooms', multiselect=True)

# Iterate through selected room numbers (they are unique, unlike room names that can be repeated within the same model) and get the corresponding room elements
selected_room_numbers = [selected.split(" - ")[0] for selected in selected_rooms_and_names] #refers only to the relement's name, for each element selected.
selected_room_names = [selected.split(" - ")[1] for selected in selected_rooms_and_names]

for selected_room_number in selected_room_numbers:

    selected_room_element = next(room for room in rooms if
                                 room.get_Parameter(BuiltInParameter.ROOM_NUMBER).AsString() == selected_room_number)
    room = doc.GetElement(selected_room_element.Id)
    print('{}------------------------------'.format(room))

    print('{}------------------------------'.format(room.Number))
    wall_finish_param = room.LookupParameter('Parede_REV_1')
    wall_finish2_param = room.LookupParameter('Parede_REV_2')
    wall_finish3_param = room.LookupParameter('Parede_REV_3')
    floor_finish_param = room.LookupParameter('Piso_REV_1')
    floor_finish2_param = room.LookupParameter('Piso_REV_2')

    ceiling_finish_param = room.LookupParameter('Forro_REV_1')
    rooms_ceiling_finish_id = room.LookupParameter('Forro_REV_1_COD')


    # The following three room builtin paramaters were chosen to store only the numeric identifiers corresponding to the finishing materials collected (100-199 for floor finishes, 200-299 for wall finishes, 300-399 for ceiling finishes)

    rooms_wall_finish_id = room.LookupParameter('ACAB PAREDE 2')
    rooms_wall_finish_id_2 = room.LookupParameter('Parede_REV_2_COD')
    rooms_wall_finish_id_3 = room.LookupParameter('Parede_REV_3_COD')

    rooms_floor_finish_id = room.LookupParameter('ACAB PAREDE 2')
    rooms_floor_finish_id_2 = room.LookupParameter('Piso_REV_2_COD')


    # Useful information about project's rooms:
    room_default_height_offset = int(3 * 3.28084)  # Value AsDouble that Equals to 2.74m
    room_upper_offset = room.get_Parameter(BuiltInParameter.ROOM_UPPER_OFFSET)
    room_level_elev = (room.Level).get_Parameter(BuiltInParameter.LEVEL_ELEV).AsDouble()
    room_upper_level = room.get_Parameter(BuiltInParameter.ROOM_UPPER_LEVEL).AsElementId()
    room_id = room.Id.ToString()
    room_name = room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()
    room_elem = doc.GetElement(ElementId(int(room_id)))
    room_area = float((room.get_Parameter(BuiltInParameter.ROOM_AREA).AsValueString())[:4])
    #print(type(room_area))

    room_bbox = room.get_BoundingBox(doc.ActiveView)
    room_outline = Outline(room_bbox.Min, room_bbox.Max)
    # Establishing rooms as filters to elements
    room_as_filter = BoundingBoxIntersectsFilter(room_outline)# Create filter
    intersecting_elem = FilteredElementCollector(doc).WherePasses(room_as_filter).ToElements() # Using filter to retrieve elements
    # list_python_collected_elements = ['room {}: {}'.format(room),list(collected_intersecting_elements)]

    for elem in intersecting_elem:
        try:
            elem_category = str(elem.Category.BuiltInCategory)
            elem_type = doc.GetElement(elem.GetTypeId())

            elem_type_name = elem_type.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
            elem_type_mark = elem_type.get_Parameter(BuiltInParameter.WINDOW_TYPE_ID).AsString()

           # elem_area = float((elem.LookupParameter('Área').AsValueString())[:5])
            #area_tolerance = (room_area * .98 < elem_area < room_area * 1.02)

            # DEFINICOES:
            if 'REV' in elem_type_name and elem in collector:
                # print('{}, {}, cód. ID {}'.format(elem.Name, elem.Category.Name, elem.Id))

                elem_structure = HostObjAttributes.GetCompoundStructure(elem_type)
                layers = elem_structure.GetLayers()

                elem_type = doc.GetElement(elem.GetTypeId())
                elem_type_description = elem_type.get_Parameter(BuiltInParameter.ALL_MODEL_DESCRIPTION).AsString()
                # print('descricao marca e nome', elem_type_description, elem_type_mark, elem_type_name)
                print('{}, in {}-{} - marca de tipo: {}'.format(elem_category, room.Number, room_name, elem_type_mark))

                if elem_category == walls_category:
                    wall_mats[elem_type_description] = type_id_str
                # elif elem_category == floors_category and area_tolerance:
                #     try:
                #         t = Transaction(doc, "applying floor finish material to room's parameter")
                #         t.Start()
                #         print('PISO:')
                #         floor_finish_param.Set(elem_type_description)
                #         rooms_floor_finish_id.Set(type_id_str)
                #         print('{} - {}'
                #               .format(type_id_str, elem_type_description))
                #     except TypeError:
                #         print('Conferir se especificação e código do elemento de piso {} estão associadas aos campos '
                #               'Descrição e Marca de tipo, respectivamente'
                #                   .format(elem_type_name))
                #     t.Commit()


        except AttributeError:
            pass

    try:

        print('PAREDE:')
        if len(wall_mats) == 0:
            print('NENHUM REVESTIMENTO DE PAREDE IDENTIFICADO')

        elif len(wall_mats) == 1:

            wall_finish1 = wall_mats.items()[0][0]
            wall_id1 = wall_mats.items()[0][1]

            t = Transaction(doc,
                               "applying additional wall finish materials and IDs to the respective room's parameter")
            t.Start()
            print('Aplicado o código referente a {}'.format(wall_finish1))
            wall_finish_param.Set(wall_finish1)
            wall_finish2_param.Set('')
            wall_finish3_param.Set('')

            rooms_wall_finish_id.Set(wall_id1)
            rooms_wall_finish_id_2.Set('')
            rooms_wall_finish_id_3.Set('')

            print('{} ({})'.format(wall_id1, wall_finish1))
            t.Commit()

        wall_mats = {}
        print('-------------------------------------------------------------------------------------------------------')

    except:
        if IndexError:
            pass
        elif AttributeError:
            print('CONFERIR: Ainda há parâmetro(s) (de código ou de descrição de revestimentos) a adicionar ao projeto.')
    rooms_total+=1
print('{} ambiente(s) analisado(s).'.format(rooms_total))
