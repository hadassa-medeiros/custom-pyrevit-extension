# -*- coding: utf-8 -*-
"""Importa esquadrias (janelas e portas) de um CSV exportado de DWG
e cria os FamilyTypes correspondentes no Revit.

Formato CSV esperado (com header):
    Codigo,Largura,Altura
    J1,1.20,1.50
    P1,0.90,2.10
"""
from pyrevit import forms
from lib import CADToRevitMigrator

doc = __revit__.ActiveUIDocument.Document

csv_path = forms.pick_file(
    file_ext="csv",
    title="Selecione o CSV de esquadrias"
)

if not csv_path:
    forms.alert("Nenhum arquivo selecionado.")
else:
    migrator = CADToRevitMigrator(csv_path, doc)

    if not migrator.esquadrias:
        forms.alert("O CSV nao contem esquadrias validas (esperado colunas: Codigo, Largura, Altura).")
    else:
        print("Esquadrias encontradas no CSV: {}".format(len(migrator.esquadrias)))
        print("Criando tipos...\n")
        created = migrator.create_all_types()
        print("\nProcesso finalizado.")
