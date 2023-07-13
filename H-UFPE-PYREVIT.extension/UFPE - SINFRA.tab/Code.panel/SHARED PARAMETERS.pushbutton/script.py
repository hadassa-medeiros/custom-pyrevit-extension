# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
import Autodesk.Revit.ApplicationServices as Application



doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application
# s = DB.DefinitionFile(
#     Application.ControlledApplication.OpenSharedParameterFile(
#         'CPATRI-SPO-UFPE_ParametrosCompartilhados.txt')
#         )
# print(s)
group_name = 'Códigos'
# def_groups = DB.DefinitionFile.Groups(group_name)
def_groupss = DB.DefinitionGroup.Definitions
create_group = DB.DefinitionGroups.Create(DB.DefinitionGroups.Name,DB.DefinitionGroups)
print(def_groupss)
print(create_group)
# open = Application.ControlledApplication.OpenSharedParameterFile
print(open)
# def_creation = DB.Definition.Create(revit.ExternalDefinitionCreationOptions('A', forgtype))
# print(def_creation)
#



# forgtype = revit.ForgeTypeId('autodesk.spec.aec:material-1.0.0')
# print(forgtype.TypeId)
#
# sp = revit.Transaction(doc, "criar parametro compartilhado")
# sp.Start()
# new_guid = def_creation.GUID
# print(new_guid)
# ex_def = revit.Definitions.Create(def_creation, new_guid)
#
# sp.Commit()
# sp.HasEnded()






