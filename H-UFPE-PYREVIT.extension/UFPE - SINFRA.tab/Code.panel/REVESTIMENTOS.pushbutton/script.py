# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

niveis_collector =    DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Levels)
materiais_collector = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Materials)
pisos_collector =     DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Floors)
forros_collector =    DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Ceilings)
paredes_collector =   DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls)
ambientes_collector = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms)

niveis = niveis_collector.WhereElementIsNotElementType().ToElements()
materiais = materiais_collector.ToElements()
ambientes = ambientes_collector.WhereElementIsNotElementType().ToElements()
pisos = pisos_collector.ToElements()
forros = forros_collector.ToElements()
paredes = paredes_collector.ToElements()
paredes_instancias = paredes_collector.WhereElementIsNotElementType().ToElements()

forros_categ = str(DB.BuiltInCategory.OST_Ceilings)
paredes_categ = str(DB.BuiltInCategory.OST_Walls)
pisos_categ = str(DB.BuiltInCategory.OST_Floors)

categorias_relevantes = [forros_categ, paredes_categ, pisos_categ]

ambientes_em_teste = []
# 1123256, 1123259, 1123262, 618033, 1123955, 1123958, 1502389, 1457753, 1457750,
# ids = [1977895, 1977898]
ids = [336972, 336975]
ids_2pav = [1456878, 1456726, 1457503, 1456893, 1966174, 1504489,
       1456890, 1456589, 1457521, 1457773,1457776, 1457779, 1456887, 1456896, 1456899, 1456902, 1456905, 1457797,
       1457791, 1456732, 1456751, 1456847, 1456884, 1456844, 1456881, 1456741, 1456741, 1456761, 1456838, 1493649,
       1457816, 1457750, 1457753]

# ids = [1502389, 1457753, 1457750] #copa mezanino
for id in ids_2pav:
    amb = doc.GetElement(DB.ElementId(id))
    ambientes_em_teste.append(amb)
print('Localizadas XYZ bounding box dos seguintes elementos:')

for amb in ambientes_em_teste:
# for amb in ambientes_em_teste:
    altura_padrao_amb_offset = int(3 * 3.28084)
    amb_lim_sup = amb.get_Parameter(DB.BuiltInParameter.ROOM_UPPER_LEVEL)
    amb_desloc_sup = amb.get_Parameter(DB.BuiltInParameter.ROOM_UPPER_OFFSET)
    amb_level = amb.Level.Name
    amb_id = amb.Id.ToString()
    amb_name = amb.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
    amb_elem = doc.GetElement(DB.ElementId(int(amb_id)))
    amb_area_str = amb.LookupParameter('Área').AsValueString()
    amb_area = float((amb_area_str)[:5])
    amb_acab_forro = amb.get_Parameter(DB.BuiltInParameter.ROOM_FINISH_CEILING)
    amb_acab_parede = amb.get_Parameter(DB.BuiltInParameter.ROOM_FINISH_WALL)
    amb_acab_piso = amb.get_Parameter(DB.BuiltInParameter.ROOM_FINISH_FLOOR)

# fator_multipl_m2_para_double = (amb.LookupParameter('Área').AsDouble()) / amb_area
    amb_bbox = amb.get_BoundingBox(doc.ActiveView)
    amb_outline = DB.Outline(amb_bbox.Min,amb_bbox.Max)  # é a outline que se passa como arg pro método DB.BoundingBoxIntersectsFilter (e não um objeto tipo BoundingBoxXYZ
    lista_mats_paredes = []
    for n in range(len(niveis)):
        try:
            nome_nivel = niveis[n].Name
            id_nivel = niveis[n].Id
            altura_absoluta_nivel = niveis[n].get_Parameter(DB.BuiltInParameter.LEVEL_ELEV).AsDouble()
            # print('A altura absoluta do nivel {} é {}'.format((niveis[n]).Name, altura_absoluta_nivel))
            pe_esquerdo_nivel = (niveis[n + 1].get_Parameter(DB.BuiltInParameter.LEVEL_ELEV).AsDouble()) - (
                niveis[n].get_Parameter(DB.BuiltInParameter.LEVEL_ELEV).AsDouble())
            # print('O pé esquerdo do pavto {} é: {}'.format(nome_nivel, pe_esquerdo_nivel))
            if id_nivel == amb.LevelId:
                # print('yes')
                t4 = DB.Transaction(doc, 'mudar limite vertical ambientes')
                t4.Start()
                # amb_lim_sup.Set(id_nivel)
                amb_desloc_sup.Set(pe_esquerdo_nivel - .7)
                t4.Commit()
        except ValueError or Exception or IndexError:
            pass

            print('offset do ambiente modifcado.')
    cod_paredes = amb.LookupParameter('COD-REV-PAREDE_1')
    cod_paredes2 = amb.LookupParameter('COD-REV-PAREDE_2')
    # cod_paredes3 = amb.LookupParameter('COD-REV-PA  REDE_3')
    cod_piso = amb.LookupParameter('COD-REV-PISO_1')
    cod_piso2 = amb.LookupParameter('COD-REV-PISO_2')
    cod_forro = amb.LookupParameter('COD-REV-TETO_1')
    print('{} - {}-{} ---------------------------------------------------'
          .format(amb_name, amb_level, amb_area))

    amb_como_filtro = DB.BoundingBoxIntersectsFilter(amb_outline)# Create filter
    elementos_intersectantes = DB.FilteredElementCollector(doc).WherePasses(amb_como_filtro).ToElements()    # Use filter to retrieve elements
    # lista_python_collected_elements = ['Ambiente {}: {}'.format(amb),list(collected_intersecting_elements)]
    print('ENCONTRADOS os seguintes objetos:')

    for elem in elementos_intersectantes:
        # SEM O TRY/EXCEPT ELE NAO CONSEGUE ITERAR POR TODOS OS ELEMENTOS:
        try:
            # DEFINIÇÕES:
            categ = str(elem.Category.BuiltInCategory)
            area_elem = float((elem.LookupParameter('Área').AsValueString())[:5])

            if any(str(elem.Category.BuiltInCategory) == categoria for categoria in categorias_relevantes):
                # print('{}, {}, cód. ID {}'.format(elem.Name, elem.Category.Name, elem.Id))
                elem_type = doc.GetElement(elem.GetTypeId())
                elem_estrut = DB.HostObjAttributes.GetCompoundStructure(elem_type)
                camadas = elem_estrut.GetLayers()

                for camada in camadas:
                    # a lista de critérios (tewmporariamente) que atuarão como filtro
                    is_camada_acabamento = any(str(
                        camada.Function.ToString()) == funcao_camada for funcao_camada in ['Finish1', 'Finish2', 'Membrane']
                                                           )
                    is_camada_zero   = camada.LayerId == 0
                    is_camada_ultima = camada.LayerId == elem_estrut.LayerCount - 1
                    conj_regras_PISO = [is_camada_acabamento, is_camada_zero]
                    #and elem_type.Width > 0.05
                    # print('a camada superficial do ambiente {} é a index {}, {}'.format(amb_name, camada.LayerId, funcao))
                    mat_rev_camada = doc.GetElement(DB.ElementId(int(camada.MaterialId.ToString())))
                    marca = mat_rev_camada.get_Parameter(DB.BuiltInParameter.ALL_MODEL_MARK).AsString()
                    tolerancia_area = (amb_area * .85 < area_elem < amb_area * 1.2)

                    possibilidades_forro = [is_camada_ultima, is_camada_acabamento, tolerancia_area]
                    if categ == paredes_categ and is_camada_acabamento:
                        # print(elem.Name, elem.Id.ToString())
                        mat_parede = mat_rev_camada
                        lista_mats_paredes.append(mat_parede.Id)
                    #                         print('material PAREDE em {}: {}'.format(amb_name, mat_parede.Name))
                    elif categ == forros_categ and tolerancia_area:
                        if any(possib == True for possib in possibilidades_forro):
                            print('o forro do ambiente {} é: {}, {}, ID nº {}'.format(amb_name, elem.Name,
                                                                                      elem.Category.Name, elem.Id))
                            mat_forro = mat_rev_camada
                            print(marca)
                            t = DB.Transaction(doc, "aplicar cod revest forro a ambiente")
                            t.Start()
                            cod_forro.Set(mat_forro.Id)
                            amb_acab_forro.Set(marca)
                            t.Commit()
                    elif categ == pisos_categ:
                        if is_camada_acabamento:
                            print('o piso do ambiente {} é: {}, ID nº {}'.format(
                            amb_name, elem.Name, elem.Id))
                            mat_piso = mat_rev_camada
                            t = DB.Transaction(doc, "aplicar cod revest piso a ambiente")
                            t.Start()
                            cod_piso.Set(mat_piso.Id)
                            amb_acab_piso.Set(marca)
                            t.Commit()
                            # print('material de piso identificado:', mat_piso.Name)
                        elif is_camada_zero and camada.Function.ToString() == 'Structure':
                            print('o piso do ambiente {} não possui acabamento, e é: {}, ID nº {}'.format(
                                amb_name, elem.Name, elem.Id))
                            mat_piso = mat_rev_camada
                            t = DB.Transaction(doc, "aplicar cod revest piso a ambiente")
                            t.Start()
                            cod_piso.Set(mat_piso.Id)
                            t.Commit()
                    # if any(condition == True for condition in conditions): #ok mas dessa forma é um OU (se satisfaz QUALQUER dos 4 critérios, ele "passa".

        except AttributeError:
            pass
    lista_mats_paredes = list(set(lista_mats_paredes))
    print(lista_mats_paredes) # ele sempre vai sobrescrever essa lista com a relação dos materiais de revestimento
    # encontrados no último ambiente pelo qual o iterador passou.
    if len(lista_mats_paredes) == 1:
        t3 = DB.Transaction(doc, "aplicar cods revest adicionais de parede ao ambiente")
        t3.Start()
        cod_paredes.Set(lista_mats_paredes[0])
        amb_acab_parede.Set(marca)
        t3.Commit()
    elif len(lista_mats_paredes) == 2:
        t3 = DB.Transaction(doc, "aplicar cods revest adicionais de parede ao ambiente")
        t3.Start()
        cod_paredes.Set(lista_mats_paredes[0])
        cod_paredes2.Set(lista_mats_paredes[1])
        t3.Commit()
    elif len(lista_mats_paredes) == 3:
        t3 = DB.Transaction(doc, "aplicar cods revest adicionais de parede ao ambiente")
        t3.Start()
        cod_paredes.Set(lista_mats_paredes[0])
        cod_paredes2.Set(lista_mats_paredes[1])
        cod_paredes3.Set(lista_mats_paredes[2])
        t3.Commit()