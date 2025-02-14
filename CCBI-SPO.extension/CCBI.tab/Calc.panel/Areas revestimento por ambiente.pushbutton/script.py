# -*- coding: utf-8 -*-
import clr
import csv
import codecs
import Autodesk.Revit.DB as DB
clr.AddReference('RevitAPI')
import os
import math

from revit_doc_interface import (
    RevitDocInterface,
    find_id_by_element_name,
    get_name,
    get_room_number
    )
import Autodesk.Revit.UI.Selection as sel
from pyrevit import forms
# from rpw import revit, db, ui, forms

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

interface = RevitDocInterface()

__title__     = "Areas Revestimentos"
__author__    = "Hadassa Medeiros"

# Definir categorias relevantes e criar filtro
relevant_categories = [
    DB.ElementCategoryFilter(cat) for cat in [
        DB.BuiltInCategory.OST_Ceilings, 
        DB.BuiltInCategory.OST_Walls, 
        DB.BuiltInCategory.OST_Floors
        ]
    ]

# Correct rooms upper limit to avoid collecting floor/wall elements from above
levels = interface.levels
room_numbers_and_names = ["{} - {}".format(
    get_room_number(room),
    # room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
    get_name(room)
) for room in list(interface.rooms)]

# Show a checkbox list for room selection
selected_rooms_and_names = forms.SelectFromList.show(room_numbers_and_names, button_name='Select Rooms', multiselect=True)

# Iterate through selected room numbers (they are unique, unlike room names that can be repeated within the same model) and get the corresponding room elements
selected_room_numbers = [selected.split(" - ")[0] for selected in selected_rooms_and_names] #refers only to the relement's name, for each element selected.
selected_room_names = [selected.split(" - ")[1] for selected in selected_rooms_and_names]

# Make output path dynamic so it works on any machine
output_path = 'C:\Users\Admin\Areas_rev_ambientes{}.csv'.format(doc.Title)
# arquivo_csv = codecs.open(output_path, 'wb', encoding='utf-8')
# escritor = csv.writer(arquivo_csv)
# escritor.writerow(['TABELA DE AREAS DE REVESTIMENTO POR AMBIENTE'])

room_data = {
    'AMBIENTE': str,
    'REVESTIMENTOS': {
        'PISOS': [.0,' m2'],
        'PAREDES': [.0,' m2'],
        'FORROS': [.0,' m2']
    }
}

# escritor.writerow([key for key in room_data.keys()])
# escritor.writerow([''] + [key for key in room_data['REVESTIMENTOS'].keys()])

for selected_room_number in selected_room_numbers:
    selected_room_element = next(room for room in interface.rooms if
                                 get_room_number(room) == selected_room_number)
    room = doc.GetElement(selected_room_element.Id)

    # Useful information about project's rooms:
    room_default_height_offset = int(3 * 3.28084)  # Value AsDouble that Equals to 2.74m
    room_upper_offset = room.get_Parameter(DB.BuiltInParameter.ROOM_UPPER_OFFSET)
    room_upper_offset_metric = float(room_upper_offset.AsDouble())/3.280840
    room_level_elev = (room.Level).get_Parameter(DB.BuiltInParameter.LEVEL_ELEV).AsDouble()
    room_upper_level = room.get_Parameter(DB.BuiltInParameter.ROOM_UPPER_LEVEL).AsElementId()
    room_id = room.Id.ToString()
    room_name = get_name(room) 
    room_bbox = room.get_BoundingBox(doc.ActiveView)
    room_outline = DB.Outline(room_bbox.Min, room_bbox.Max)
    # Establishing rooms as filters to elements
    room_as_filter = DB.BoundingBoxIntersectsFilter(room_outline)# Create filter
    intersecting_elem = DB.FilteredElementCollector(doc).WherePasses(room_as_filter).ToElements() # Using filter to retrieve elements
    # list_python_collected_elements = ['room {}: {}'.format(room),list(collected_intersecting_elements)]

    for level in levels:
        try:
            level_above = levels[levels.index(level) + 1]
            level_above_elev = level_above.get_Parameter(DB.BuiltInParameter.LEVEL_ELEV).AsDouble()
            floor_to_floor_height = level_above_elev - room_level_elev # This value is in the Revit's format AsDouble, not in meters.
            new_rooms_upper_offset = floor_to_floor_height - .7
            new_rooms_upper_offset_metric = new_rooms_upper_offset/3.280840
            if room.Level.Id == level.Id and floor_to_floor_height > 0:
                t = DB.Transaction(doc, "Change room's upper offset value in meters")
                t.Start()
                room_upper_offset.Set(new_rooms_upper_offset)
                t.Commit()
                # print("Altura do ambiente {} corrigida de {}m para {}m.".format(room_name, room_upper_offset_metric, round(new_rooms_upper_offset_metric,3)))
        except IndexError:
            pass

    room_area = float(room.get_Parameter(DB.BuiltInParameter.ROOM_AREA).AsValueString()[:4])
    room_bounding_box = room.get_BoundingBox(doc.ActiveView)
    room_outline = DB.Outline(room_bounding_box.Min, room_bounding_box.Max)
    # Establishing room limits as filters to elements (A filter used to match elements with a bounding box that intersects the given Outline https://www.revitapidocs.com/2023/1fbe1cff-ed94-4815-564b-05fd9e8f61fe.htm)
    is_within_room_space = DB.BoundingBoxIntersectsFilter(room_outline)# Create filter
    combined_categories_filter = DB.LogicalOrFilter(relevant_categories)
   # add filter to ignore layer which FUnction is not Finish1 or Finish2 in the elements compound structure
    combined_filter = DB.LogicalAndFilter([
    is_within_room_space,
    combined_categories_filter
])
    room_data['AMBIENTE'] = '{} - {}'.format(selected_room_number, room_name)
    # room_data['NOME'] = room_name
    # room_data['AREA'] = room_area

    elements_intersected_by_room = DB.FilteredElementCollector(doc).WherePasses(combined_filter).ToElements() # Using filter to retrieve elements
    for e in elements_intersected_by_room:
        #quero que ele so colete pisos q tenham layer com function == Finish2
        elem_type = doc.GetElement(e.GetTypeId())
        elem_layers = elem_type.GetCompoundStructure().GetLayers()
        elem_category = e.get_Parameter(DB.BuiltInParameter.ELEM_CATEGORY_PARAM).AsValueString().upper()
       
        for layer in elem_layers:
            if any(str(layer.Function) == v for v in ['Finish1', 'Finish2']):
                elem_area =  float(e.get_Parameter(DB.BuiltInParameter.HOST_AREA_COMPUTED).AsValueString().split(' ')[0])
                # print(float(elem_area.split(' ')[0]), ' - ', e.Name, e.Id)

                # elem_area = "{:.1f}".format(elem_area)  # Isso vai garantir que seja arredondado para 1 casa decimal como string
                # elem_area = math.ceil(elem_area * 10) / 10
                print(elem_area, ' - ', e.Name, e.Id)

                room_data['REVESTIMENTOS'][elem_category][0] += elem_area
                # print(valor_ceil, ' - ', e.Name, e.Id)
        # from pprint import pprint
        # for k,v in room_data.items():
        #     pprint(v)

    # escritor.writerow(
        # [room_data['AMBIENTE']] + 
        # ['{:.2f}'.format(round(v[0],2)) for v in room_data['REVESTIMENTOS'].values()])
    room_data = {
        'AMBIENTE': str,
        'REVESTIMENTOS': {
            'PISOS': [.0,' m2'],
            'PAREDES': [.0,' m2'],
            'FORROS': [.0,' m2']
        }
    }
# arquivo_csv.close()
# os.startfile(output_path)


# end of 1st part of filtering process
# now, "enter" the structure of each intersecting wall/floor/ceiling element
    # check only for Finish2 (or Finish1?) layer functions (ignore the others)
    # extra: double check to see if layer has a valid finishing material assigned to it
    
    #for each room in the project
    #   for each element that passed both filtering phases
        # get its area and add it to the respective area counter
        # store the following information in a dictionary:
            #   room number, name and area
            #   finishing name + total area sum + category(wall,floor,ceiling)

    # write the data in a csv file and save it