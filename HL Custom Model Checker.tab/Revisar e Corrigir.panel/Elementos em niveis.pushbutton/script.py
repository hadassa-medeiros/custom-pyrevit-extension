# -*- coding: utf-8 -*-
from revit_doc_interface import (RevitDocInterface, double_to_metric, remove_acentos)
import operator
import csv
from pyrevit import forms
from custom_forms import CustomInput
import Autodesk.Revit.DB as DB
doc = __revit__.ActiveUIDocument.Document

__title__     = "Elementos associados a níveis"
__author__    = "Hadassa Medeiros"
__doc__       = "Verifica se ha elementos incorretamente associados a um respectivo nível/pavimento"

interface = RevitDocInterface()


# def filter_by(category):
#     return DB.ElementCategoryFilter(DB.BuiltInCategory.category)
room_elem_filter = DB.ElementCategoryFilter(DB.BuiltInCategory.OST_Rooms)
floor_elem_filter = DB.ElementCategoryFilter(DB.BuiltInCategory.OST_Floors)
wall_elem_filter = DB.ElementCategoryFilter(DB.BuiltInCategory.OST_Walls)
ceiling_elem_filter = DB.ElementCategoryFilter(DB.BuiltInCategory.OST_Ceilings) 
door_elem_filter = DB.ElementCategoryFilter(DB.BuiltInCategory.OST_Doors)
window_elem_filter = DB.ElementCategoryFilter(DB.BuiltInCategory.OST_Windows)

dict_category_filters_by_name = {
    "Ambiente": room_elem_filter,
    "Piso": floor_elem_filter, 
    "Parede": wall_elem_filter,
    "Forro": ceiling_elem_filter, 
    "Porta": door_elem_filter,
    "Janela": window_elem_filter 
}

dict_levels_by_name = {level.Name: level for level in interface.levels}

# pede para o usuario selecionar um nivel
selected_level = forms.CommandSwitchWindow.show(
    [key for key in dict_levels_by_name.keys()], 
    message="Selecione um nível para verificar os elementos associados"
)

selected_category = forms.CommandSwitchWindow.show(
    [key for key in dict_category_filters_by_name.keys()],
    message="Selecione uma categoria de elementos para verificar os associados ao piso selecionado"
)

if selected_level and selected_category:
    level = dict_levels_by_name[selected_level]
    level_name = remove_acentos(selected_level)
    level_elevation = double_to_metric(level.Elevation)
    # level_elevation = "{:.2f}".format(level_elevation)
    # level_elevation = level_elevation.replace(".", ",")
    room_elem_filter = dict_category_filters_by_name[selected_category]

    # pega todos os elementos associados ao nivel
    dependent_elements = level.GetDependentElements(room_elem_filter)
    elements_count = len(dependent_elements)

    for elem_id in dependent_elements:
        elem = doc.GetElement(elem_id)
        name = elem.Name
        if elem.get_Parameter(DB.BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId() == level.Id:
            print(name)
        
    print('Ha {} elementos de {} associados ao pavimento {}'.format(elements_count, selected_category, selected_level)) 


#regra: se o pavimento nao for ossatura, nao deve haver Paredes associadas a ele atraves do parametro WALL_BASE_CONSTRAINT 

    # # cria um csv com os elementos associados ao nivel
    # csv_path = 
    # interface.create_csv_file(
    #     "Elementos associados ao nível {}".format(level_name),
    #     ["Elemento", "Categoria", "Nível", "Elevação"]
    # )

    # with open(csv_path, 'w', newline='') as csvfile:
    #     csvwriter = csv.writer(csvfile)
    #     csvwriter.writerow(["Elemento", "Categoria", "Nível", "Elevação"])

    #     for element in elements:
    #         element_name = element.Name
    #         element_category = element.Category.Name
    #         element_level = element.get_Parameter(
    #             "Nível"
    #         ).AsValueString()
    #         element_elevation = element.get_Parameter(
    #             "Elevação"
    #         ).AsDouble()
    #         element_elevation = double_to_metric(element_elevation)
    #         element_elevation = "{:.2f}".format(element_elevation)
    #         element_elevation = element_elevation.replace(".", ",")

    #         csvwriter.writerow([
    #             element_name, element_category, element_level, element_elevation
    #         ])

    # # mostra o csv ao usuario
    # forms.alert(
    #     "Foram encontrados {} elementos associados ao nível {} (Elevação: {} m)."
    #     .format(elements_count, level_name, level_elevation),
    #     ok=True,
    #     exitscript=True
    # )
