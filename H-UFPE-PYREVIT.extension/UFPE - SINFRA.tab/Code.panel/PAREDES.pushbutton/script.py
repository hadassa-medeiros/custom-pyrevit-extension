# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application
meter_to_double = 3.2808399
paredes_collector = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls)
niveis_collector =    DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Levels)
pisos_collector =     DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Floors)
paredes = paredes_collector.ToElements()
niveis = niveis_collector.WhereElementIsNotElementType().ToElements()
pisos = pisos_collector.ToElements()
piso = doc.GetElement(DB.ElementId(2031165))
floor_thickness = piso.get_Parameter(DB.BuiltInParameter.FLOOR_ATTR_THICKNESS_PARAM)
# print(floor_thickness.AsValueString())

levels_ids = []
levels_ascend_order = []
for n in range(len(niveis)): # this instead of for level in levels assures ascendent order for the project levels.
    try:
        nome_nivel = niveis[n].Name
        id_nivel = niveis[n].Id
        only_guide_level = niveis[n].LookupParameter('NIVEL GUIA')
        altura_absoluta_nivel = niveis[n].get_Parameter(DB.BuiltInParameter.LEVEL_ELEV).AsDouble()
        altura_metros_nivel = altura_absoluta_nivel / meter_to_double
        print(only_guide_level.AsInteger())
        levels_ascend_order.append(altura_absoluta_nivel)
        levels_ids.append(id_nivel)

        # levels_ascend_order.update({altura_absoluta_nivel: int(id_nivel.ToString())})
        print('A altura absoluta do nivel {} é {}m'.format((niveis[n]).Name, altura_metros_nivel))
        pe_esquerdo_nivel = (
                            niveis[n + 1].get_Parameter(DB.BuiltInParameter.LEVEL_ELEV).AsDouble()) \
                            - (niveis[n].get_Parameter(DB.BuiltInParameter.LEVEL_ELEV).AsDouble()
                            )
        # print('O pé esquerdo do pavto {} é: {}'.format(nome_nivel, pe_esquerdo_nivel))
    except ValueError or Exception or IndexError:
        pass

levels_ascend_order = sorted(levels_ascend_order)
print(levels_ascend_order)
# print(levels_ids)
# Sort dict by value
# levels_ascend_order = sorted(levels_ascend_order.items())
# print(levels_ascend_order) #list of tuples

wall = doc.GetElement(DB.ElementId(480864))
is_top_attached = wall.get_Parameter(DB.BuiltInParameter.WALL_TOP_IS_ATTACHED) #Boolean, read only.
restr_sup = wall.get_Parameter(DB.BuiltInParameter.WALL_HEIGHT_TYPE) #ElementId of level above
restr_sup_elem_id = int(restr_sup.AsElementId().ToString())
elem_restr_sup = doc.GetElement(DB.ElementId(restr_sup_elem_id))

restr_base = wall.get_Parameter(DB.BuiltInParameter.WALL_BASE_CONSTRAINT) ##ElementId of current level
restr_base_elem_id = int(restr_base.AsElementId().ToString())
elem_restr_base = doc.GetElement(DB.ElementId(restr_base_elem_id))
elev_restr_base = elem_restr_base.get_Parameter(DB.BuiltInParameter.LEVEL_ELEV).AsDouble()

desl_sup = wall.get_Parameter(DB.BuiltInParameter.WALL_TOP_OFFSET) # Double
ext_base = wall.get_Parameter(DB.BuiltInParameter.WALL_BOTTOM_EXTENSION_DIST_PARAM)


# IDEIA ABORTADA: MELHOR DICIONARIO COM ID_NIVEL: ALTURA_ELEVACAO e iterar pelos pares key value apenas desse dicionario. o prob foi deixar na ordem crescente.
for h in levels_ascend_order:
    index_number = levels_ascend_order.index(h)
    print(index_number)
    if h == elev_restr_base:
        print('ok',id)
        h_level_above = levels_ascend_order[index_number+2]
        h_level_above = altura_absoluta_nivel
        .get_Parameter(DB.BuiltInParameter.LEVEL_ELEV).AsDouble()
        print(h_level_above)
        # t = DB.Transaction(doc, "attach wall top")
        # t.Start()
        # restr_sup.Set(level_above)
        # t.Commit()

# PRA VOLTAR A USAR O ID COMO FORMA DE IDENTIFICAR O NIVEL QUE SE QUER TER COMO RESTRIÇAO SUPERIOR DAS PAREDES
# for id in levels_ids:
#     if id == restr_base.AsElementId():
#         print('ok',id)
#         level_above = levels_ids[position+1]
#         t = DB.Transaction(doc, "attach wall top")
#         t.Start()
#         restr_sup.Set(level_above)
#         t.Commit()
# ext_base.Set(-.15 * meter_to_double)
# desl_sup.Set(-.11 * meter_to_double)

# print(is_top_attached, restr_sup.AsValueString(), restr_base.AsValueString(), desl_sup.AsDouble(), ext_base.AsDouble())
