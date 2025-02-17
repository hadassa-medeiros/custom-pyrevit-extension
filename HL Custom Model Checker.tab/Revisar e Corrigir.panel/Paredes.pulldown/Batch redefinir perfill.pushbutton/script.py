'''
This tool intends to solve a frequent deviation from CCBI's modelling standards
When using wall systems in layers, one for the structure and another for the finishing,
the finishing layer must have its geometry united to the base wall, which automatically accounts for
window and door openings in both wall elements of the system. 
The button allows to batch redefine unneeded profile sketching made as an incorrect/unnecessary workaround,
so the model is more consistent with the standards and the model review process is more efficient.
'''
import clr
import Autodesk.Revit.DB as DB
clr.AddReference('RevitAPI')

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

def get_selected_elements(uidoc):
    return [uidoc.Document.GetElement(elem_id) for elem_id in uidoc.Selection.GetElementIds()] 

for selected in get_selected_elements(uidoc):
    #if SketchId is not -1, then it is has been modified and must be reset if created to account for door/window openings
     # open a transaction to make it be -1

    if selected.SketchId != -1:
        print(selected.Name)
        try:
            t = DB.Transaction(doc, "Reset SketchId")
            t.Start()
            selected.RemoveProfileSketch()
            t.Commit()
        except Exception as e:
            print("Erro ao resetar SketchId para o elemento {}: {}".format(selected.Name, e))
            pass
    # print(selected.Name)