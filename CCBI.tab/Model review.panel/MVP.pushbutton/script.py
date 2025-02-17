# -*- coding: utf-8 -*-

from pyrevit import revit, script
import Autodesk.Revit.DB as DB

# Criar um output no console do PyRevit
output = script.get_output()

# Abrir o documento atual do Revit
doc = __revit__.ActiveUIDocument.Document

# Parâmetros de checagem
TAMANHO_MAX_FAMILIA_KB = 500  # Exemplo: famílias acima de 500 KB são consideradas pesadas
NOMES_INVALIDOS = ["Familia1", "SemNome", "Default"]  # Exemplo de nomes incorretos
CATEGORIAS_PERMITIDAS = ["Walls", "Floors", "Doors", "Windows"]  # Categorias aceitáveis

# Identificar famílias pesadas
def verificar_familias_pesadas():
    familias_pesadas = []
    for fam in DB.FilteredElementCollector(doc).OfClass(DB.Family):
        if fam.IsEditable:
            tamanho_kb = 0 / 1024  # Converter para KB
            if tamanho_kb > TAMANHO_MAX_FAMILIA_KB:
                familias_pesadas.append((fam.Name, tamanho_kb))
    return familias_pesadas

# Verificar nomes inválidos
def verificar_nomes_invalidos():
    nomes_errados = []
    for fam in DB.FilteredElementCollector(doc).OfClass(DB.Family):
        if fam.Name in NOMES_INVALIDOS:
            nomes_errados.append(fam.Name)
    return nomes_errados

# Verificar categorias erradas
def verificar_categorias_invalidas():
    categorias_erradas = []
    for elem in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
        if elem.Category and elem.Category.Name not in CATEGORIAS_PERMITIDAS:
            categorias_erradas.append(elem.Category.Name)
    return list(set(categorias_erradas))

# Rodar todas as verificações
output.print_md("🚀 **Rodando análise do modelo...**")

familias_pesadas = verificar_familias_pesadas()
nomes_errados = verificar_nomes_invalidos()
categorias_erradas = verificar_categorias_invalidas()

# Exibir resultados
if familias_pesadas:
    output.print_md("🔴 **Famílias muito pesadas:**")
    for nome, tamanho in familias_pesadas:
        output.print_md("- {}: {} KB".format(nome, round(tamanho, 2)))

if nomes_errados:
    output.print_md("⚠️ **Famílias com nomes inválidos:**")
    for nome in nomes_errados:
        output.print_md("- {nome}")

if categorias_erradas:
    output.print_md("⚠️ **Elementos em categorias inválidas:**")
    for categoria in categorias_erradas:
        output.print_md("-{}".format(categoria))

if not (familias_pesadas or nomes_errados or categorias_erradas):
    output.print_md("✅ **Nenhum problema encontrado!**")

output.print_md("🚀 **Análise concluída!**")
