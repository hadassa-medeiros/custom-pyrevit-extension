# -*- coding: utf-8 -*-
import clr
import csv
import subprocess
import Autodesk.Revit.DB as DB
clr.AddReference('RevitAPI')

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

output_path = 'C:\Users\Hadassa\Documents\UFPE-SPO-CCBI\Relatorios\Areas_rev_ambientes{}.csv'.format(doc.Title)
arquivo_csv = open(output_path, 'w')
escritor = csv.writer(arquivo_csv)
escritor.writerow(['Numero','Nome', 'Nome revestimento', 'Area revestimento', 'Categoria'])

data_by_room = {
    'Numero': 00,
    'Nome': '',
    'Area': 0,
    'Revestimentos': {'Pisos': [], 'Paredes': [], 'Forros': []}
    # 'Pisos': 0,
    # 'Forro': 0
}

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
                print("Altura do ambiente {} corrigida de {}m para {}m.".format(room_name, room_upper_offset_metric, round(new_rooms_upper_offset_metric,3)))
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
    data_by_room['Numero'] = selected_room_number
    data_by_room['Nome'] = room_name
    data_by_room['Area'] = room_area

    escritor.writerow([
        data_by_room['Numero'], data_by_room['Nome'], data_by_room['Area']
                        ])
   
    elements_intersected_by_room = DB.FilteredElementCollector(doc).WherePasses(combined_filter).ToElements() # Using filter to retrieve elements
    for e in elements_intersected_by_room:
        #quero que ele so colete pisos q tenham layer com function == Finish2
        elem_type = doc.GetElement(e.GetTypeId())
        elem_layers = elem_type.GetCompoundStructure().GetLayers()
        elem_category = e.get_Parameter(DB.BuiltInParameter.ELEM_CATEGORY_PARAM).AsValueString()
        for layer in elem_layers:
            if any(str(layer.Function) == v for v in ['Finish1', 'Finish2']):
                elem_area = float(
                    e.get_Parameter(
                        DB.BuiltInParameter.HOST_AREA_COMPUTED
                        ).AsValueString()
                        .split(' ')[0]
                        )
                print(elem_area, 'must equal')

                data_by_room['Categoria'] = elem_category

                data_by_room['Revestimentos']['Paredes'].append({e.Name: elem_area})
                for key,value in data_by_room['Revestimentos'].items():
                    # escritor.writerow([key, [v[0] for v in value]])
                # for key,value in ...data_by_room['Revestimentos']
                #     escritor.writerow([
                #         data_by_room['Categoria'],

                #         ])
                # for item in data_by_room['Revestimentos']['Paredes']:
                #     escritor.writerow([item.keys])
                    #gerar csv relatorio
arquivo_csv.close()
import os

os.startfile(output_path)

        # print(type(elem_compound_structure))
        
        
        # print([[type(layer.LayerId), str(layer.Function)] for layer in elem_layers])
        # print(e.get_Parameter(DB.BuiltInParameter.HOST_AREA_COMPUTED).AsValueString())

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



#     #Objeto que ira armazenar soma total de areas por revestimento encontrado no ambiente,
#     # nas respectivas categorias relevantes
#     wall_area_count_by_room = 0

#     # transformar em dicionario contendo nome do ambiente, contagem total associada a revestimento encontrado e a categoria especifica
#     # a qual pertence (forro/teto, piso ou parede)
#     total_areas_by_finishing_material = {
#         'Ambiente': str,
#         'Piso': [{}],
#         'Parede': [{}],
#         'Forro': [{}]
#     }
    
#     for elem in intersecting_elem:
#         try:
#             elem_category = elem.Category.DB.BuiltInCategory
#             elem_type = doc.GetElement(elem.GetTypeId())

#             elem_type_name = elem_type.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
#             elem_area = float((elem.LookupParameter('Área').AsValueString())[:5])
#             def is_relevant_category_and_inside_room():
#                 if elem_category == 'OST_Floors' and room_area * .97 < elem_area < room_area * 1.03:
#                     return True
#                 elif elem_category == 'OST_Walls' or elem_category == 'OST_Ceilings':
#                     return True
#                 else:
#                     return False
                
#             if 'REV' in elem_type_name or 'SPO' in elem_type_name and is_relevant_category_and_inside_room():
#                 # print('{}, {}, cód. ID {}'.format(elem.Name, elem.Category.Name, elem.Id))
#                 elem_structure = DB.HostObjAttributes.GetCompoundStructure(elem_type)
#                 layers = elem_structure.GetLayers()
#                 elem_type = doc.GetElement(elem.GetTypeId())
#                 elem_type_description = elem_type.get_Parameter(DB.BuiltInParameter.ALL_MODEL_DESCRIPTION).AsString()
#                 elem_area = float(elem.get_Parameter(DB.BuiltInParameter.HOST_AREA_COMPUTED).AsValueString().split(' ')[0])
#                 # print('descricao marca e nome', elem_type_description, elem_type_mark, elem_type_name)
#                 # print('{}, in {}-{} - marca de tipo: {}'.format(elem_category, room.Number, room_name, elem_type_mark))
#                 if elem_category == DB.BuiltInCategory.OST_Walls:
#                     wall_area_count_by_room = wall_area_count_by_room + elem_area
#                     print('Area total acumulada do revestimento de parede: ', wall_area_count_by_room)

#                 elif elem_category == DB.BuiltInCategory.OST_Floors:

#         except AttributeError:
#             pass