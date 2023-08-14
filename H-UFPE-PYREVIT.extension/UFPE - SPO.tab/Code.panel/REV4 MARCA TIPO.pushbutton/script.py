# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
import Autodesk.Revit.UI.Selection as sel
from pyrevit import forms
# from rpw import revit, db, ui, forms

import clr
clr.AddReference('RevitAPIUI')


__title__     = "Revestimentos por ambiente"
__author__    = "Hadassa Medeiros"
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument


# doc = uidoc.Document
app = __revit__.Application

levels_collector =    DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Levels)
materials_collector = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Materials)
floors_collector =     DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Floors)
ceilings_collector =    DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Ceilings)
walls_collector =   DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls)
rooms_collector = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms)

levels = list(levels_collector.WhereElementIsNotElementType().ToElements())
materials = materials_collector.ToElements()
rooms = list(rooms_collector.WhereElementIsNotElementType().ToElements())
floors = floors_collector.ToElements()
ceilings = ceilings_collector.ToElements()
walls = walls_collector.ToElements()
walls_instances = walls_collector.WhereElementIsNotElementType().ToElements()

ceilings_category = str(DB.BuiltInCategory.OST_Ceilings)
walls_category = str(DB.BuiltInCategory.OST_Walls)
floors_category = str(DB.BuiltInCategory.OST_Floors)

relevant_categories = [ceilings_category, walls_category, floors_category]

wall_materials_ids_list = []
wall_materials_in_room = []
wall_mats = {}
info_per_room = {}
double_to_meter_divisor = 3.28084


room_numbers_and_names = ["{} - {}".format(
    room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString(),
    room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
) for room in rooms]

# Show a checkbox list for room selection

selected_rooms_and_names = forms.SelectFromList.show(room_numbers_and_names, button_name='Select Rooms', multiselect=True)

# Iterate through selected room names and get the corresponding room elements
selected_room_names = [selected.split(" - ")[1] for selected in selected_rooms_and_names] #refers only to the relement's name, for each element selected.


for selected_room_name in selected_room_names:
    selected_room_element = next(room for room in rooms if
                                 room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString() == selected_room_name)
    print('-------------------------------',selected_room_name,'-------------------------------')
    room = doc.GetElement(selected_room_element.Id)
    wall_finish_param = room.LookupParameter('_REV_PAREDE_1')
    wall_finish2_param = room.LookupParameter('_REV_PAREDE_2')
    wall_finish3_param = room.LookupParameter('_REV_PAREDE_3')
    floor_finish_param = room.LookupParameter('_REV_PISO_1')
    floor_finish2_param = room.LookupParameter('_REV_PISO_2')
    ceiling_finish_param = room.LookupParameter('_REV_FORRO_1')

    # Useful information about project's rooms:
    room_default_height_offset = int(3 * 3.28084)  # Value AsDouble that Equals to 2.74m
    room_upper_offset = room.get_Parameter(DB.BuiltInParameter.ROOM_UPPER_OFFSET)
    room_level_elev = (room.Level).get_Parameter(DB.BuiltInParameter.LEVEL_ELEV).AsDouble()
    room_upper_level = room.get_Parameter(DB.BuiltInParameter.ROOM_UPPER_LEVEL).AsElementId()
    room_id = room.Id.ToString()
    room_name = room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
    room_elem = doc.GetElement(DB.ElementId(int(room_id)))
    room_area_str = room.LookupParameter('Área').AsValueString()
    room_area = float((room_area_str)[:5])

    print('Pé direito: {}m'.format(room_upper_offset.AsValueString()))
    # The following three room builtin paramaters were chosen to store only the numeric identifiers corresponding to the finishing materials collected (100-199 for floor finishes, 200-299 for wall finishes, 300-399 for ceiling finishes)
    rooms_ceiling_finish_id = room.get_Parameter(DB.BuiltInParameter.ROOM_FINISH_CEILING)

    rooms_wall_finish_id = room.get_Parameter(DB.BuiltInParameter.ROOM_FINISH_WALL)
    rooms_wall_finish_id_2 = room.LookupParameter('ACAB PAREDE 2')
    rooms_wall_finish_id_3 = room.LookupParameter('ACAB PAREDE 3')

    rooms_floor_finish_id = room.get_Parameter(DB.BuiltInParameter.ROOM_FINISH_FLOOR)
    rooms_floor_finish_id_2 = room.LookupParameter('ACAB PISO 2')

    room_bbox = room.get_BoundingBox(doc.ActiveView)
    room_outline = DB.Outline(room_bbox.Min, room_bbox.Max)
    # Establishing rooms as filters to elements
    room_as_filter = DB.BoundingBoxIntersectsFilter(room_outline)# Create filter
    intersecting_elem = DB.FilteredElementCollector(doc).WherePasses(room_as_filter).ToElements() # Using filter to retrieve elements
    # list_python_collected_elements = ['room {}: {}'.format(room),list(collected_intersecting_elements)]

    for elem in intersecting_elem:
        try:
            elem_category = str(elem.Category.BuiltInCategory)
            elem_type = doc.GetElement(elem.GetTypeId())

            elem_type_name = elem_type.get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
            elem_area = float((elem.LookupParameter('Área').AsValueString())[:5])
            area_tolerance = (room_area * .9 < elem_area < room_area * 1.1)

            # DEFINICOES:
            if 'REV' in elem_type_name or elem_category == ceilings_category:
                # print('{}, {}, cód. ID {}'.format(elem.Name, elem.Category.Name, elem.Id))

                elem_structure = DB.HostObjAttributes.GetCompoundStructure(elem_type)
                layers = elem_structure.GetLayers()

                elem_type = doc.GetElement(elem.GetTypeId())
                elem_type_description = elem_type.get_Parameter(DB.BuiltInParameter.ALL_MODEL_DESCRIPTION).AsString()

                type_id = elem_type.get_Parameter(DB.BuiltInParameter.WINDOW_TYPE_ID)
                type_id_str = elem_type.get_Parameter(DB.BuiltInParameter.WINDOW_TYPE_ID).AsString()
                # print('{}, in {}-{} - marca de tipo: {}'.format(elem_category, room.Number, room_name, type_id_str))

                if elem_category == walls_category:
                    wall_mats[elem_type_description] = type_id_str

                elif elem_category == floors_category and area_tolerance:
                    print('OK', elem_type_description, type_id_str)
                    t = DB.Transaction(doc, "applying floor finish material to room's parameter")
                    t.Start()
                    floor_finish_param.Set(elem_type_description)
                    rooms_floor_finish_id.Set(type_id_str)
                    print('O código {} referente ao acabamento de piso {} foi aplicado ao ambiente {}'.format(type_id_str,
                                                                                                              elem_type_description,
                                                                                                              room_name))
                    t.Commit()

                for layer in layers:
                    # The list of general criteria that will work as a filter to collect the wanted layers (finishing layers) of each construction element:
                    is_layer_finish = any(str(layer.Function.ToString()) == layer_function for layer_function in ['Finish1', 'Finish2', 'Membrane'])
                    is_layer_last = (layer.LayerId == elem_structure.LayerCount - 1)
                    is_layer_zero = layer.LayerId == 0

                    # Combination of criteria for a layers' material to be collected as finishing material in a room's ceiling element:
                    ceiling_possibilities = [is_layer_finish, is_layer_last]

                    if elem_category == ceilings_category:
                        if any(possibility == True for possibility in ceiling_possibilities):
                            t = DB.Transaction(doc, "applying ceiling finish material to room's parameter")
                            t.Start()
                            ceiling_finish_param.Set(elem_type_description)
                            rooms_ceiling_finish_id.Set(type_id_str)
                            print('O código {} referente ao acabamento de forro {} foi aplicado ao ambiente {}'.format(type_id_str,
                                                                                                                       elem_type_description,
                                                                                                                       room_name))
                            t.Commit()


        except AttributeError:
            pass

    try:
        print('------------Revestimentos de parede identificados:-----------------')

        if len(wall_mats) == 1:

            wall_finish1 = wall_mats.items()[0][0]
            wall_id1 = wall_mats.items()[0][1]

            t = DB.Transaction(doc,
                               "applying additional wall finish materials and IDs to the respective room's parameter")
            t.Start()
            wall_finish_param.Set(wall_finish1)
            wall_finish2_param.Set('')
            wall_finish3_param.Set('')

            rooms_wall_finish_id.Set(wall_id1)
            rooms_wall_finish_id_2.Set('')
            rooms_wall_finish_id_3.Set('')

            print('Aplicado o código {} ({})'.format(wall_id1, wall_finish1))
            t.Commit()

        elif len(wall_mats) == 2:

            wall_finish1 = wall_mats.items()[0][0]
            wall_finish2 = wall_mats.items()[1][0]

            wall_id1 = wall_mats.items()[0][1]
            wall_id2 = wall_mats.items()[1][1]
            t = DB.Transaction(doc,
                               "applying additional wall finish materials and IDs to the respective room's parameter")

            t.Start()
            wall_finish_param.Set(wall_finish1)
            wall_finish2_param.Set(wall_finish2)
            wall_finish3_param.Set('')
            rooms_wall_finish_id.Set(wall_id1)
            rooms_wall_finish_id_2.Set(wall_id2)
            rooms_wall_finish_id_3.Set('')
            print('Aplicados os códigos {} ({}), {} ({})'.format(wall_id1, wall_finish1, wall_id2, wall_finish2))
            t.Commit()

        elif len(wall_mats) == 3:

            wall_finish1 = wall_mats.items()[0][0]
            wall_finish2 = wall_mats.items()[1][0]
            wall_finish3 = wall_mats.items()[2][0]

            wall_id1 = wall_mats.items()[0][1]
            wall_id2 = wall_mats.items()[1][1]
            wall_id3 = wall_mats.items()[2][1]

            t = DB.Transaction(doc,
                               "applying additional wall finish materials and IDs to the respective room's parameter")
            t.Start()
            wall_finish_param.Set(wall_finish1)
            wall_finish2_param.Set(wall_finish2)
            wall_finish3_param.Set(wall_finish3)
            rooms_wall_finish_id.Set(wall_id1)
            rooms_wall_finish_id_2.Set(wall_id2)
            rooms_wall_finish_id_3.Set(wall_id3)
            print('Aplicados os códigos {} ({}), {} ({}), {} ({})'.format(wall_id1, wall_finish1, wall_id2, wall_finish2, wall_id3, wall_finish3))
            t.Commit()

    except IndexError:
        pass
