# from _base import *
# import _snippets as sn
# import csv

# __title__  = "Generate Report"
# __author__ = "hadassa.lima@ufpe.br"


# c = sn.ElementCollections()

# walltypes = [sn.get_name(wall) for wall in c.get_types("walls")]

# # print("{} tipos de parede no projeto ".format(len(walltypes)))

# # Conferir ambientes:
# """ comparar lista de ambientes por pavimento de csv
# quantidade deve ser igual
# para cada ambiente, numero e nome deve ser igual ao csv data
# caso nao, add comentario de revisao com msg equivalente (numero incorreto, nome incorreto) """

# with open('name.csv', newline='') as csvfile:
#     spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
#     for row in spamreader:
#         print(', '.join(row))
