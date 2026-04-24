# -*- coding: utf-8 -*-
import os
import sys

SCRIPT_DIR = os.path.dirname(__file__)
EXTENSION_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
if EXTENSION_ROOT not in sys.path:
    sys.path.insert(0, EXTENSION_ROOT)

from shared_lib import (
    Convert,
    Model,
    create_walltype_whith_one_layer_and_given_thickness,
    is_vertical,
    is_horizontal,
    is_diagonal,
    get_distance_between_lines,
    distance_between_lines_is_acceptable,
    get_longest_line,
    get_shortest_line,
    create_wall,
)

convert = Convert()
model = Model(__revit__.ActiveUIDocument)

doc = model.doc
wall_width = .15

vertical_lines = [line for line in model.lines if is_vertical(line)]
horizontais = [line for line in model.lines if is_horizontal(line)]
diagonais = [line for line in model.lines if is_diagonal(line)]
dist_minima_em_cm_entre_duas_linhas_paralelas = .4

activeLevel = doc.ActiveView.GenLevel
wt = create_walltype_whith_one_layer_and_given_thickness(doc, model.walltypes, .4)
