# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from pyrevit import forms

doc = __revit__.ActiveUIDocument.Document
collector = DB.FilteredElementCollector(doc)

# # allow user to work on all levesl at once or one at a time
# selected_rooms_and_names = forms.SelectFromList.show(room_numbers_and_names, button_name='Select Rooms', multiselect=True)

# 1. PHASE OF ALL ELEMENTS SHOULD BE 'LEVANTAMENTO'
def get_phase_id_by_name(doc, phase_name):
    phases = DB.FilteredElementCollector(doc).OfClass(DB.Phase).ToElements()
    for phase in phases:
        if phase.Name == phase_name:
            return phase.Id
    return None

target_phase_created = 'LEVANTAMENTO'
target_phase_created_id = get_phase_id_by_name(doc, target_phase_created)

def get_phase_created(elem):
    return elem.get_Parameter(DB.BuiltInParameter.PHASE_CREATED)
    
def correct_elem_phase(elem, target_phase_created_id):
    incorrect_phase_created = get_phase_created(elem).AsValueString()

    t = DB.Transaction(doc, "Correct created phase parameter")
    t.Start()
    try:
        param = elem.get_Parameter(DB.BuiltInParameter.PHASE_CREATED)
        param.Set(target_phase_created_id)  # Define a altura (em metros)
        print(
            "Fase da elemento ID {} corrigida de {} para {}"
              .format(element.Id, incorrect_phase_created, target_phase_created_id)
              )
    except Exception as e:
        print("Error: {}".format(e))
        pass
    t.Commit()

# all_phased_elements = collector.OfCategory(
#     DB.BuiltInCategory.OST_elements
#     ).WhereElementIsNotElementType()
param_phase_created = DB.ElementId(DB.BuiltInParameter.PHASE_CREATED)
param_phase_demolished = DB.ElementId(DB.BuiltInParameter.PHASE_DEMOLISHED)

rule_phase_created = DB.ParameterFilterRuleFactory.CreateHasValueParameterRule(param_phase_created)
rule_phase_demolished = DB.ParameterFilterRuleFactory.CreateHasValueParameterRule(param_phase_demolished)

filter_has_phases_param = DB.ElementParameterFilter([rule_phase_created, rule_phase_demolished])

phased_elements = collector.WherePasses(filter_has_phases_param).ToElements()

for elem in phased_elements:
    phase_created = elem.get_Parameter(DB.BuiltInParameter.PHASE_CREATED)
    phase_demolished = elem.get_Parameter(DB.BuiltInParameter.PHASE_DEMOLISHED)
    
    created_phase_name = phase_created.AsValueString() if phase_created else "None"
    demolished_phase_name = phase_demolished.AsValueString() if phase_demolished else "None"
    
    # print(
    #     "Elemento {} | ID {} | Fase Criada: {} | Fase Demolida: {}".format(elem.Name, elem.Id, created_phase_name, demolished_phase_name)
    # )

def are_elements_in_incorrect_phase(elements_list, target_phase_created_id):
    elements_in_incorrect_phase = []
    for element in elements_list:
        phase_created_id = get_phase_created(element).AsElementId()
        phase_created_name = get_phase_created(element).AsValueString()

        if phase_created_id != target_phase_created_id:
            element_type = element.get_Parameter(
            DB.BuiltInParameter.ELEM_FAMILY_AND_TYPE_PARAM
            ).AsValueString()
            print(
            "Elemento em fase incorreta ({}): {} (ID: {})"
            .format(phase_created_name, element_type, element.Id)
            )
            elements_in_incorrect_phase.append(element)
    return elements_in_incorrect_phase

are_elements_in_incorrect_phase(phased_elements, target_phase_created_id)

def batch_correct_elements_phase(elements_list, target_phase_created_id):
    for element in elements_list:
        correct_elem_phase(element, target_phase_created_id)

    if len(elements_list) == 1:
        print(
        "{} elemento detectado fora da fase {} foi corrigido'."
        .format(len(elements_list), target_phase_created)
        )
    elif len(elements_list) > 1:
        print('_'*50)
        print(
            "{} elementos detectados fora da fase {} foram corrigidos."
            .format(len(elements_list), target_phase_created)
            )
    else:
        print(
            "Todos os elementos estão na fase '{}'!".format(target_phase_created)
            )    

# batch_correct_elements_phase(elements_in_incorrect_phase, target_phase_created_id)
'''
2. ALL WALLS SHOULD
HAVE THEIR BASE CONSTRAINT SET TO '{level}_Ossatura' 
and TOP CONSTRAINT SET TO '{level_above}_Ossatura' 
and ATTACH TOP TO FLOOR ABOVE
and name according to the following pattern:
    {ALV or EST or REV or ''+_}{MATERIAL OF EXTERNAL LAYER}_{MATERIAL OF MIDDLE LAYER}_{MATERIAL OF INTERIOR LAYER}_{TOTAL WIDTH IN CM}CM, separator == _
and if wall is REV
    compound structure should have only one layer
    compound structure's layer.Function should be 'Finish2'
    compound structure's layer.Material should not be -1 (means empty/None/no material assigned)
    layer.Material should not be -1 (means empty/None/no material assigned)
and if wall is ALV or EST
    core compound structure's layer.Function should be 'Structure'
    layer.Material should not be -1 (means empty/None/no material assigned)
'''