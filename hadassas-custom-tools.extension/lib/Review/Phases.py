# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from pyrevit import forms
from Review.WriteReview import write_review_comments

doc = __revit__.ActiveUIDocument.Document
collector = DB.FilteredElementCollector(doc)

def get_phase_created(elem):
    return elem.get_Parameter(DB.BuiltInParameter.PHASE_CREATED)

def get_phase_id_by_name(phase_name):
    for phase in DB.FilteredElementCollector(doc).OfClass(DB.Phase).ToElements():
        if phase.Name == phase_name:
            return phase.Id

def filter_elems_with_phase_created_param():
    rule_phase_created = DB.ParameterFilterRuleFactory.CreateHasValueParameterRule(
         DB.ElementId(DB.BuiltInParameter.PHASE_CREATED)
         )
    has_phase_created_filter = DB.ElementParameterFilter(rule_phase_created)
    return collector.WherePasses(has_phase_created_filter).ToElements()

def correct_elem_phase(elem, elem_phase_created_param_obj, target_phase_created_id):
    t = DB.Transaction(doc, "Corrigir fase criada")
    t.Start()
    try:
        elem_phase_created_param_obj.Set(target_phase_created_id)
    except Exception as e:
        print(e)
    t.Commit()

def review_phase_created(target_phase_created_name):
    target_phase_created_id = get_phase_id_by_name(target_phase_created_name)
    
    elems_in_incorrect_phase = {}

    for elem in filter_elems_with_phase_created_param():
        phase_created = elem.get_Parameter(DB.BuiltInParameter.PHASE_CREATED)
        phase_created_name = phase_created.AsValueString() if phase_created else None

        if phase_created_name != target_phase_created_name:
            category_name = elem.Category.Name if elem.Category else "Sem Categoria"
            elem_name = elem.Name
            write_review_comments(elem, "Fase incorreta ({}), deveria ser {}".format(phase_created_name, target_phase_created_name))

            # Inicializar estrutura do dicionário
            if category_name not in elems_in_incorrect_phase:
                elems_in_incorrect_phase[category_name] = {}
            if elem_name not in elems_in_incorrect_phase[category_name]:
                elems_in_incorrect_phase[category_name][elem_name] = []

            elems_in_incorrect_phase[category_name][elem_name].append(elem)

    if elems_in_incorrect_phase:
        print("\nElementos em fase incorreta:\n")
        for category, elems_by_name in elems_in_incorrect_phase.items():
            print("Categoria: {}".format(category))
            for name, elems in elems_by_name.items():
                print("  {}: {} elemento(s)".format(name, len(elems)))
        
        # Mostrar confirmação ao usuário
        confirm = forms.alert(
            "Foram encontrados elementos fora da fase '{}'.\nDeseja corrigir automaticamente?".format(target_phase_created_name),
            title="Corrigir Fases?",
            ok=True,
            cancel=True
        )
        
        if confirm:
            for category, elems_by_name in elems_in_incorrect_phase.items():
                for name, elems in elems_by_name.items():
                    for elem in elems:
                        phase_created = elem.get_Parameter(DB.BuiltInParameter.PHASE_CREATED)
                        correct_elem_phase(elem, phase_created, target_phase_created_id)
                        write_review_comments(elem, "Fase corrigida")

            forms.alert("Fases corrigidas com sucesso.", title="Concluído")
        else:
            forms.alert("Nenhuma alteração foi feita.", title="Cancelado")

review_phase_created("LEVANTAMENTO")