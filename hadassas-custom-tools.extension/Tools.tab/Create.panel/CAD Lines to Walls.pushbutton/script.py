from revit_doc_interface import (RevitDocInterface, get_elem_param)

doc = __revit__.ActiveUIDocument.Document
interface = RevitDocInterface()
# access lines of layer Paredes from imported CAD file
def get_cad_lines_to_walls():
    cad_lines = interface.lines
    print('cad_lines:', cad_lines)
    # cad_layer = cad_lines
    
    # if cad_layer:
    #     cad_lines = interface.get_cad_lines_from_layer(cad_layer)
    
    return cad_lines

get_cad_lines_to_walls(doc, 'Paredes')