# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from pyrevit import forms

doc = __revit__.ActiveUIDocument.Document
collector = DB.FilteredElementCollector(doc)

def get_phase_created(elem):
        return elem.get_Parameter(DB.BuiltInParameter.PHASE_CREATED)

def get_phase_id_by_name(phase_name):
    for phase in DB.FilteredElementCollector(doc).OfClass(DB.Phase).ToElements():
        if phase.Name == phase_name:
            return phase.Id

def filter_elements_which_have_phase_created_parameter():
    rule_phase_created = DB.ParameterFilterRuleFactory.CreateHasValueParameterRule(
         DB.ElementId(DB.BuiltInParameter.PHASE_CREATED)
         )
    has_phase_created_filter = DB.ElementParameterFilter(rule_phase_created)
    return collector.WherePasses(has_phase_created_filter).ToElements()

def correct_elem_phase(elem, elem_phase_created_param_obj, target_phase_created_id):
    t = DB.Transaction(doc, "Correct created phase parameter")
    t.Start()
    try:
        print('Corrigindo {} de {} para'.format(
            elem.Name, 
            elem_phase_created_param_obj.AsValueString()
            )
        )
        elem_phase_created_param_obj.Set(target_phase_created_id)
        print(elem_phase_created_param_obj.AsValueString())
    except Exception as e:
        print(e)
        pass
    t.Commit()
# # allow user to work on all levesl at once or one at a time
# selected_rooms_and_names = forms.SelectFromList.show(room_numbers_and_names, button_name='Select Rooms', multiselect=True)

# 1. PHASE OF ALL ELEMENTS SHOULD BE 'LEVANTAMENTO'
def phase_created_is(target_phase_created_name):
    target_phase_created_id = get_phase_id_by_name(target_phase_created_name)
    
    elements_in_incorrect_phase = []

    for elem in filter_elements_which_have_phase_created_parameter():
        # phase_created_param = DB.BuiltInParameter.PHASE_CREATED
        phase_created = elem.get_Parameter(DB.BuiltInParameter.PHASE_CREATED)
        phase_created_name = phase_created.AsValueString() if phase_created else None
        phase_demolished = elem.get_Parameter(DB.BuiltInParameter.PHASE_DEMOLISHED)
        phase_demolished_name = phase_demolished.AsValueString() if phase_demolished else None
        
        # print(
        #     "Elemento {} | ID {} | Fase Criada: {} | Fase Demolida: {}".format(elem.Name, elem.Id, created_phase_name, demolished_phase_name)
        # )

        # correct_parameter_value(elem, phase_created_param, target_phase_created_id)
        if phase_created_name != target_phase_created_name:
            elements_in_incorrect_phase.append(elem)

            print('{} - {} - Fase {}'.format(
                elem.Name, 
                elem.Category.Name, 
                phase_created_name
            ))
            
            # inserir botao de confirmacao para corrigir o modelo ou nao
            # correct_elem_phase(elem, phase_created, target_phase_created_id)
        
    if len(elements_in_incorrect_phase) > 0:
        print('{} elementos em fase incorreta (deveria ser {})'.format(
        len(elements_in_incorrect_phase), 
        target_phase_created_name
    ))

    # def batch_correct_elements_phase(elements_list, target_phase_created_id):
    #     for element in elements_list:
    #         correct_elem_phase(element, target_phase_created_id)

    #     if len(elements_list) == 1:
    #         print(
    #         "{} elemento detectado fora da fase {} foi corrigido'."
    #         .format(len(elements_list), target_phase_created)
    #         )
    #     elif len(elements_list) > 1:
    #         print('_'*50)
    #         print(
    #             "{} elementos detectados fora da fase {} foram corrigidos."
    #             .format(len(elements_list), target_phase_created)
    #             )
    #     else:
    #         print(
    #             "Todos os elementos estão na fase '{}'!".format(target_phase_created)
    #             )    