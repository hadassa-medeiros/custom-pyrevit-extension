# -*- coding: utf-8 -*-

from collections import defaultdict
from pyrevit import revit, script
import Autodesk.Revit.DB as DB
from revit_doc_interface import (RevitDocInterface, get_name)   

# Abrir o documento atual do Revit
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
interface = RevitDocInterface()

def contar_paredes_perfil_editado():
    contagem_paredes = defaultdict(int)  # Dicionário para contar por nome
    total_paredes_perfil_editado = 0
    for wall in interface.walls:
        rooms_intersected = []

        if str(wall.SketchId) != '-1':  # Se tem perfil modificado
            wall_bbox = wall.get_BoundingBox(None)
            wall_outline = DB.Outline(wall_bbox.Min, wall_bbox.Max)  # Bounding box da parede
            # Criar um filtro de interseção
            wall_as_filter = DB.BoundingBoxIntersectsFilter(wall_outline)
            # Verificar interseção com cada ambiente
            for room in interface.rooms:
                if wall_as_filter.PassesFilter(room):  # Verifica a interseção
                    rooms_intersected.append(room)                    
            print(
                "{} ID {}"
                .format(wall.Name, wall.Id)
                )
            if len(rooms_intersected) > 0:
                print("Intersecta com os ambientes:")
                print([get_name(room) for room in rooms_intersected])
            contagem_paredes[wall.Name] += 1
            total_paredes_perfil_editado += 1
           
    if not contagem_paredes:
        print("Nenhuma parede com perfil modificado foi encontrada.")
    else:
        print("{} paredes com perfil modificado encontradas:".format(total_paredes_perfil_editado))
        for nome, quantidade in contagem_paredes.items():
            print("{} do tipo '{}'".format(quantidade, nome))

contar_paredes_perfil_editado()


# # Criar um output no console do PyRevit
# output = script.get_output()

# # Parâmetros de checagem
# TAMANHO_MAX_FAMILIA_KB = 500  # Exemplo: famílias acima de 500 KB são consideradas pesadas
# NOMES_INVALIDOS = ["Familia1", "SemNome", "Default"]  # Exemplo de nomes incorretos
# CATEGORIAS_PERMITIDAS = ["Walls", "Floors", "Doors", "Windows"]  # Categorias aceitáveis

# # Identificar famílias pesadas
# def verificar_familias_pesadas():
#     familias_pesadas = []
#     for fam in DB.FilteredElementCollector(doc).OfClass(DB.Family):
#         if fam.IsEditable:
#             tamanho_kb = 0 / 1024  # Converter para KB
#             if tamanho_kb > TAMANHO_MAX_FAMILIA_KB:
#                 familias_pesadas.append((fam.Name, tamanho_kb))
#     return familias_pesadas

# # Verificar nomes inválidos
# def verificar_nomes_invalidos():
#     nomes_errados = []
#     for fam in DB.FilteredElementCollector(doc).OfClass(DB.Family):
#         if fam.Name in NOMES_INVALIDOS:
#             nomes_errados.append(fam.Name)
#     return nomes_errados

# # Verificar categorias erradas
# def verificar_categorias_invalidas():
#     categorias_erradas = []
#     for elem in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
#         if elem.Category and elem.Category.Name not in CATEGORIAS_PERMITIDAS:
#             categorias_erradas.append(elem.Category.Name)
#     return list(set(categorias_erradas))

# # Rodar todas as verificações
# output.print_md("🚀 **Rodando análise do modelo...**")

# familias_pesadas = verificar_familias_pesadas()
# nomes_errados = verificar_nomes_invalidos()
# categorias_erradas = verificar_categorias_invalidas()

# # Exibir resultados
# if familias_pesadas:
#     output.print_md("🔴 **Famílias muito pesadas:**")
#     for nome, tamanho in familias_pesadas:
#         output.print_md("- {}: {} KB".format(nome, round(tamanho, 2)))

# if nomes_errados:
#     output.print_md("⚠️ **Famílias com nomes inválidos:**")
#     for nome in nomes_errados:
#         output.print_md("- {nome}")

# if categorias_erradas:
#     output.print_md("⚠️ **Elementos em categorias inválidas:**")
#     for categoria in categorias_erradas:
#         output.print_md("-{}".format(categoria))

# if not (familias_pesadas or nomes_errados or categorias_erradas):
#     output.print_md("✅ **Nenhum problema encontrado!**")

# output.print_md("🚀 **Análise concluída!**")
