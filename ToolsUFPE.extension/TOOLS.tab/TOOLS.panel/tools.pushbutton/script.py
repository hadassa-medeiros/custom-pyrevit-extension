from _base import * # pyright: ignore[reportMissingImports]
import _snippets as sn # pyright: ignore[reportMissingImports]


for i in sn.get_selected():
    print(sn.get_name(i))