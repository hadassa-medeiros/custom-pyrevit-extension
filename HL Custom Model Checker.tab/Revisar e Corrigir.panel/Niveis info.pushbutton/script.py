# -*- coding: utf-8 -*-
from revit_doc_interface import (RevitDocInterface, double_to_metric, remove_acentos)
import operator
import csv
from pyrevit import forms
from custom_forms import CustomInput

__title__     = "Nomes, cotas e quantidade de pavimentos"
__author__    = "Hadassa Medeiros"
__doc__       = "Verifica se os nomes dos níveis estão corretos, se as cotas estão corretas e se a quantidade de pavimentos está correta."

# print(dir(forms))
# dynamic_path
# escritor = csv.writer(open("C:/Users/rafae/Desktop/levels.csv", "w", newline=''))

interface = RevitDocInterface()

# pergunta quantos pavimentos tem a edificacao representada pelo modelo
prompt_message = "Conforme o levantamento de {}, quantos níveis deve haver neste projeto, fora a Coberta?".format(interface.doc.Title)

win = CustomInput(prompt_message)
win.ShowDialog()
ref_levels_count_input_str = win.input_text # Recolhe o valor digitado pelo usuário

try:
    levels_count_input = int(ref_levels_count_input_str)
except ValueError:
    forms.alert("Entrada inválida! Por favor, insira um número.", exitscript=False)


level_names_and_elevations = {}

for level in interface.levels:
    # level_names_and_elevations[remove_acentos(level.Name).capitalize()] = str(
    #     '{:.2f}'.format(double_to_metric(level.Elevation))
    #     )
        level_names_and_elevations[remove_acentos(level.Name).capitalize()] = double_to_metric(level.Elevation)

        
sorted_level_names_and_elevations = sorted(level_names_and_elevations.items(), key=operator.itemgetter(1))
proj_levels_count = len(level_names_and_elevations)
ref_levels_count = 2+(2*levels_count_input) # adiciona Rua e Coberta ao input do usuario e dois niveis por pavimento (ossatura e piso acabado)

print("Ha {} niveis no modelo".format(proj_levels_count))
if proj_levels_count != ref_levels_count:
    print("A quantidade de pavimentos no modelo ({}) nao corresponde à esperada ({})"
          .format(proj_levels_count, ref_levels_count))

for item in sorted_level_names_and_elevations:
    print('{}m - {}'.format(item[1], item[0]))

# regras que niveis devem seguir
ordered_default_level_names = ['rua', 'terreo-ossatura', 'terreo', [], 'coberta']

# o primeiro nivel deve se chamar Rua
try:
    assert sorted_level_names_and_elevations[0][0] == ordered_default_level_names[0].capitalize()
except AssertionError:
    print("O primeiro nivel deveria se chamar 'Rua', mas se chama '{}'"
          .format(sorted_level_names_and_elevations[0][0]))

# para cada nivel, deve haver nivel-Ossatura


# o segundo nivel deve se chamar Terreo_ossatura
try:
    assert sorted_level_names_and_elevations[1][0] == ordered_default_level_names[1].capitalize()
except AssertionError:
    print("O segundo nivel deveria se chamar 'Terreo-Ossatura', mas se chama '{}'".format(sorted_level_names_and_elevations[1][0]))

# o segundo nivel deve se chamar Terreo
try:
    assert sorted_level_names_and_elevations[2][0] == ordered_default_level_names[2].capitalize()
except AssertionError:
    print("O terceiro nivel deveria se chamar 'Terreo', mas se chama '{}'".format(sorted_level_names_and_elevations[2][0])) 

# o ultimo nivel deve se chamar Coberta
try:
    assert sorted_level_names_and_elevations[-1][0] == ordered_default_level_names[-1].capitalize()
except AssertionError:
    print("O ultimo nivel deveria se chamar 'Coberta', mas se chama '{}'"
          .format(sorted_level_names_and_elevations[-1][0]))