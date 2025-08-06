from _base import * # pyright: ignore[reportMissingImports]
import _snippets as sn # pyright: ignore[reportMissingImports]
import csv

__title__  = ""
__author__ = "hadassa.lima@ufpe.br"


c = sn.ElementCollections()

# Conferir ambientes:
""" comparar lista de ambientes por pavimento de csv
quantidade deve ser igual
para cada ambiente, numero e nome deve ser igual ao csv data
caso nao, add comentario de revisao com msg equivalente (numero incorreto, nome incorreto) """

with open('name.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in spamreader:
        print(', '.join(row))