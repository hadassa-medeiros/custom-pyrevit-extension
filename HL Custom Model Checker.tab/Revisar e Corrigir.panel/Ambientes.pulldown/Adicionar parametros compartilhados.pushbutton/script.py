# -*- coding: utf-8 -*-
import os
import clr

clr.AddReference('RevitAPI')
import Autodesk.Revit.DB as DB
from pyrevit import forms

__title__ = "Adicionar parametros"
__author__ = "Codex"

doc = __revit__.ActiveUIDocument.Document
app = __revit__.Application

sp_path = forms.pick_file(file_ext='txt')
if not sp_path:
    forms.alert('Arquivo de parametros nao selecionado.', exitscript=True)

orig_path = app.SharedParametersFilename
app.SharedParametersFilename = sp_path
sp_file = app.OpenSharedParameterFile()
if sp_file is None:
    forms.alert('Arquivo de parametros compartilhados invalido.', exitscript=True)

cats = app.Create.NewCategorySet()
cats.Insert(doc.Settings.Categories.get_Item(DB.BuiltInCategory.OST_Rooms))

param_group = DB.BuiltInParameterGroup.PG_DATA

trans = DB.Transaction(doc, 'Adicionar parametros compartilhados')
trans.Start()
for grp in sp_file.Groups:
    for definition in grp.Definitions:
        binding = app.Create.NewInstanceBinding(cats)
        if not doc.ParameterBindings.Insert(definition, binding, param_group):
            doc.ParameterBindings.ReInsert(definition, binding, param_group)
trans.Commit()

app.SharedParametersFilename = orig_path
