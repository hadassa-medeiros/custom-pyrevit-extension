from _base import * # pyright: ignore[reportMissingImports]
import _snippets as sn # pyright: ignore[reportMissingImports]

__title__  = "Conferir paredes"
__author__ = "hadassa.lima@ufpe.br"

c = sn.ElementCollections()

walltypes = [sn.get_name(wall) for wall in c.get_types("walls")]

# print("{} tipos de parede no projeto ".format(len(walltypes)))
