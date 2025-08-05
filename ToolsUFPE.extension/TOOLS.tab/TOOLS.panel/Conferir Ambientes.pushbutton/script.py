from _base import * # pyright: ignore[reportMissingImports]
import _snippets as sn # pyright: ignore[reportMissingImports]

__title__  = ""
__author__ = "hadassa.lima@ufpe.br"

c = sn.ElementCollections()

# for wall in c.map_to_elem_types("walls"):
    # print(wall)
# for i in sn.get_selected():

walltypes = [sn.get_name(wall) for wall in c.get_types("walls")]

print("{} tipos de parede no projeto ".format(len(walltypes)))


# devem ser usados Pilares Estruturais, e nao colunas arquitetonicas, para evitar
# incorrecao na área e volume total das paredes 

# Conferir ambientes:
""" comparar lista de ambientes por pavimento de csv
quantidade deve ser igual
para cada ambiente, numero e nome deve ser igual ao csv data
caso nao, add comentario de revisao com msg equivalente (numero incorreto, nome incorreto) """