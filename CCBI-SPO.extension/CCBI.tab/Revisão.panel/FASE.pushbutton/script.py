# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB

doc = __revit__.ActiveUIDocument.Document
collector = DB.FilteredElementCollector(doc)

def get_phase_id_by_name(doc, phase_name):
    phases = DB.FilteredElementCollector(doc).OfClass(DB.Phase).ToElements()
    for phase in phases:
        if phase.Name == phase_name:
            return phase.Id
    return None

target_phase_name = 'LEVANTAMENTO'
target_phase_id = get_phase_id_by_name(doc, target_phase_name)

def get_phase_created_id(elem):
    return elem.get_Parameter(DB.BuiltInParameter.PHASE_CREATED).AsElementId()
    
def correct_elem_phase(elem):
    incorrect_phase_created = get_phase_created_id(elem)

    t = DB.Transaction(doc, "Correct created phase parameter")
    t.Start()
    try:
        param = elem.get_Parameter(DB.BuiltInParameter.PHASE_CREATED)
        param.Set(target_phase_id)  # Define a altura (em metros)
        print(
            "Fase da parede ID {} corrigida de {} para {}"
              .format(wall.Id, incorrect_phase_created, target_phase_id)
              )
    except Exception as e:
        print("Error: {}".format(e))
        pass
    t.Commit()

all_walls = collector.OfCategory(
    DB.BuiltInCategory.OST_Walls
    ).WhereElementIsNotElementType()

walls_in_incorrect_phase = []

for wall in all_walls:
    phase_created_id = wall.get_Parameter(
        DB.BuiltInParameter.PHASE_CREATED
        ).AsElementId()
    if phase_created_id != target_phase_id:
        wall_type = wall.get_Parameter(
            DB.BuiltInParameter.ELEM_FAMILY_AND_TYPE_PARAM
            ).AsValueString()
        print(
            "Parede em fase criada incorreta '{}': {} (ID: {})"
            .format(target_phase_name, wall_type, wall.Id)
        )
        walls_in_incorrect_phase.append(wall)
        correct_elem_phase(wall)
if len(walls_in_incorrect_phase) == 1:
    print(
        "{} parede detectada fora da fase {} foi corrigida'."
        .format(len(walls_in_incorrect_phase), target_phase_name)
        )
elif len(walls_in_incorrect_phase) > 1:
    print(
        "{} paredes detectadas fora da fase {} foram corrigidas'."
        .format(len(walls_in_incorrect_phase), target_phase_name)
        )
else:
    print(
        "Todas as paredes estão na fase '{}'!".format(target_phase_name)
        )