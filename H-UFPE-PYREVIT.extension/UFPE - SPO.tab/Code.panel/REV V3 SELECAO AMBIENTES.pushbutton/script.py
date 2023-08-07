# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
import Autodesk.Revit.UI as UI
from Autodesk.Revit.UI.Selection import ObjectType
from pyrevit import forms


from rpw.ui.forms import (FlexForm, Label, ComboBox, TextBox, TextBox,Separator, Button, CheckBox)
import clr
clr.AddReference('RevitAPIUI')


__title__     = "Revestimentos por ambiente"
__author__    = "Hadassa Medeiros"
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
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

double_to_meter_divisor = 3.28084


# INSERIR CAIXA DE DIALOGO PRA O USUARIO SELECIONAR OS AMBIENTES AOS QUAIS QUER APLICAR O SCRIPT.



picked_elements = uidoc.Selection.PickObjects(ObjectType.Element, "Selecione os ambientes:")

for p in picked_elements:
    room = doc.GetElement(p.ElementId)

    wall_finish = room.LookupParameter('REV_PAREDE_1')
    wall_finish2 = room.LookupParameter('REV_PAREDE_2')
    wall_finish3 = room.LookupParameter('REV_PAREDE_3')
    floor_finish = room.LookupParameter('REV_PISO_1')
    floor_finish2 = room.LookupParameter('REV_PISO_2')
    ceiling_finish = room.LookupParameter('REV_FORRO_1')

    # Useful information about project's rooms:
    room_default_height_offset = int(3 * 3.28084)  # Value AsDouble that Equals to 2.74m
    room_upper_offset = room.get_Parameter(DB.BuiltInParameter.ROOM_UPPER_OFFSET)
    # print(room_upper_offset.AsValueString(), floor_finish.AsValueString())
    room_level_elev = (room.Level).get_Parameter(DB.BuiltInParameter.LEVEL_ELEV).AsDouble()
    room_upper_level = room.get_Parameter(DB.BuiltInParameter.ROOM_UPPER_LEVEL).AsElementId()
    room_id = room.Id.ToString()
    room_name = room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
    room_elem = doc.GetElement(DB.ElementId(int(room_id)))
    room_area_str = room.LookupParameter('Área').AsValueString()
    room_area = float((room_area_str)[:5])

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
            # DEFINICOES:
            elem_category = str(elem.Category.BuiltInCategory)
            area_elem = float((elem.LookupParameter('Área').AsValueString())[:5])

            if any(str(elem.Category.BuiltInCategory) == categoria for categoria in relevant_categories):
                # print('{}, {}, cód. ID {}'.format(elem.Name, elem.Category.Name, elem.Id))
                elem_type = doc.GetElement(elem.GetTypeId())
                elem_structure = DB.HostObjAttributes.GetCompoundStructure(elem_type)
                layers = elem_structure.GetLayers()
                # print('{}, in {}-{}'.format(elem_category, room.Number, room_name))

                for layer in layers:
                    layers_material = doc.GetElement(DB.ElementId(int(layer.MaterialId.ToString())))
                    material_mark = layers_material.get_Parameter(DB.BuiltInParameter.ALL_MODEL_MARK).AsString()
                    # The list of general criteria that will work as a filter to collect the wanted layers (finishing layers) of each construction element:
                    is_layer_finish = any(str(layer.Function.ToString()) == layer_function for layer_function in ['Finish1', 'Finish2', 'Membrane'])
                    is_layer_last = (layer.LayerId == elem_structure.LayerCount - 1)
                    is_layer_zero = layer.LayerId == 0
                    # The list of element type specific criteria (floor, in this case), depending if it is a floor, a ceiling or a wall object.                                          )
                    area_tolerance = (room_area * .9 < area_elem < room_area * 1.1)

                    # Combination of criteria for a layers' material to be collected as finishing material in a room's ceiling element.
                    floor_possibilities = [is_layer_finish, is_layer_zero]
                    ceiling_possibilities = [is_layer_finish, is_layer_last]

                    if elem_category == walls_category and is_layer_finish:
                        # print(elem.Name, elem.Id.ToString())
                        wall_material = layers_material
                        wall_materials_in_room.append(wall_material)

                    elif elem_category == ceilings_category:
                        if any(possibility == True for possibility in ceiling_possibilities):
                            # print('The ceiling in the room named {} is: {}, {}, ID # {}'.format(room_name, elem.Name, elem.Category.Name, elem.Id))
                            ceiling_material = layers_material
                            t = DB.Transaction(doc, "applying ceiling finish material to room's parameter")
                            t.Start()
                            ceiling_finish.Set(ceiling_material.Id)
                            rooms_ceiling_finish_id.Set(material_mark)
                            t.Commit()

                            print('Material mark number {} successfuly applied'.format(material_mark))
                    elif elem_category == floors_category:
                        if is_layer_finish:
                            # print("Room {}'s floor is: {}, ID # {}".format(room_name, elem.Name, elem.Id))
                            floor_material = layers_material
                            t = DB.Transaction(doc, "applying floor finish material to room's parameter")
                            t.Start()
                            floor_finish.Set(floor_material.Id)
                            rooms_floor_finish_id.Set(material_mark)
                            t.Commit()
                            # the alternative below doesn't work for projects in which the structural layer of the floor is below the level where the room is placed, because the room's bounding box will have it's bottom surface above where the top surface of the structural floor, in other words the floor object will be outside the bounding box limits of the room, thus won't be counted as an intersecting element.
                        elif is_layer_zero and layer.Function.ToString() == 'Structure':
                            print("Room {}'s floor has no finish layer: {}, ID # {}".format(
                                room_name, elem.Name, elem.Id))
                            floor_material = layers_material
                            t = DB.Transaction(doc, "applying floor finish material to room's parameter")
                            t.Start()
                            floor_finish.Set('')
                            rooms_floor_finish_id.Set('')
                            t.Commit()

        except AttributeError:
            pass

    wall_materials_in_room = list(set(wall_materials_in_room))
    print(wall_materials_in_room)
    # Applying wall materials to respective parameters in the cases of one or many wall finishes by room.
    try:
        if len(wall_materials_in_room) == 0:
            t = DB.Transaction(doc, "applying wall finish material to the respective room's parameter")
            t.Start()
            rooms_wall_finish_id.Set('')
            t.Commit()

        if len(wall_materials_in_room) == 1:
            material_mark = (wall_materials_in_room[0]).get_Parameter(DB.BuiltInParameter.ALL_MODEL_MARK).AsString()

            t = DB.Transaction(doc, "applying additional wall finish material to the respective room's parameter")
            t.Start()
            wall_finish.Set(wall_materials_in_room[0].Id)
            rooms_wall_finish_id.Set(material_mark)
            t.Commit()

        elif len(wall_materials_in_room) == 2:
            material_mark = (wall_materials_in_room[0]).get_Parameter(DB.BuiltInParameter.ALL_MODEL_MARK).AsString()
            material_mark2 = (wall_materials_in_room[1]).get_Parameter(DB.BuiltInParameter.ALL_MODEL_MARK).AsString()

            t3 = DB.Transaction(doc, "applying additional wall finish material to the respective room's parameter")
            t3.Start()
            wall_finish.Set((wall_materials_in_room[0]).Id)
            wall_finish2.Set((wall_materials_in_room[1]).Id)
            rooms_wall_finish_id.Set(material_mark)
            rooms_wall_finish_id_2.Set(material_mark2)
            # wall_finish3.Set(wall_materials_list[2])
            t3.Commit()
        elif len(wall_materials_in_room) == 3:
            material_mark = (wall_materials_in_room[0]).get_Parameter(DB.BuiltInParameter.ALL_MODEL_MARK).AsString()
            material_mark2 = (wall_materials_in_room[1]).get_Parameter(DB.BuiltInParameter.ALL_MODEL_MARK).AsString()
            material_mark3 = (wall_materials_in_room[2]).get_Parameter(DB.BuiltInParameter.ALL_MODEL_MARK).AsString()

            t3 = DB.Transaction(doc, "applying additional wall finish material to the respective room's parameter")
            t3.Start()
            wall_finish.Set((wall_materials_in_room[0]).Id)
            wall_finish2.Set((wall_materials_in_room[1]).Id)
            wall_finish3.Set((wall_materials_in_room[2]).Id)
            rooms_wall_finish_id.Set(int(material_mark))
            rooms_wall_finish_id_2.Set(material_mark2)
            rooms_wall_finish_id_3.Set(material_mark3)

            t3.Commit()
    except AttributeError:
        print('Algum dos parâmetros compartilhados de revestimento de parede não foi inserido como parâmetro de projeto')
        break
    # Clearing the list of wall materials after going through each room.
    wall_materials_ids_list = []
    wall_materials_in_room = []

    print('Finished')

def set_room_offset(doc):
    wall_materials_in_room = []
    wall_materials_ids_list = []

    room_name = [room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString() for room in rooms]

    # task_dialog = UI.TaskDialog('Select rooms')
    # task_dialog.Show('Revit')
    picked_elements = uidoc.Selection.PickObjects(ObjectType.Element, "Selecione os ambientes:")


