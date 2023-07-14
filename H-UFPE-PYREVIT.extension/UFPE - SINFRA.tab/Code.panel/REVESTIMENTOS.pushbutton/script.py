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
todos_elem_constr = [pisos_collector, forros_collector, paredes_collector]
ambientes_em_teste = []
# ids = [1123256, 1123259, 1123262, , 618033, 1123955, 1123958]
ids = [1502389, 1457753, 1457750] #copa mezanino

for id in ids:
    amb = doc.GetElement(DB.ElementId(id))
    ambientes_em_teste.append(amb)
print('Localizadas XYZ bounding box dos seguintes elementos:')

for amb in ambientes:
# for amb in ambientes_em_teste:
    altura_padrao_amb_offset = int(3 * 3.28084)
    amb_lim_sup = amb.get_Parameter(DB.BuiltInParameter.ROOM_UPPER_LEVEL)
    amb_desloc_sup = amb.get_Parameter(DB.BuiltInParameter.ROOM_UPPER_OFFSET)
    lista_mats_paredes = []
    amb_level = amb.Level.Name
    amb_id = amb.Id.ToString()
    amb_name = amb.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
    amb_elem = doc.GetElement(DB.ElementId(int(amb_id)))
    amb_area_str = amb.LookupParameter('Área').AsValueString()
    amb_area = float((amb_area_str)[:5])
    # fator_multipl_m2_para_double = (amb.LookupParameter('Área').AsDouble()) / amb_area
    amb_bbox = amb.get_BoundingBox(doc.ActiveView)
    amb_outline = DB.Outline(amb_bbox.Min,amb_bbox.Max)  # é a outline que se passa como arg pro método DB.BoundingBoxIntersectsFilter (e não um objeto tipo BoundingBoxXYZ

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
    cod_paredes3 = amb.LookupParameter('COD-REV-PAREDE_3')
    cod_piso = amb.LookupParameter('COD-REV-PISO_1')
    cod_piso2 = amb.LookupParameter('COD-REV-PISO_2')
    cod_forro = amb.LookupParameter('COD-REV-TETO_1')
    print('{} - {}-{} ---------------------------------------------------'
          .format(amb_name, amb_level, amb_area))

    amb_como_filtro = DB.BoundingBoxIntersectsFilter(amb_outline)# Create filter
    elementos_intersectantes = DB.FilteredElementCollector(doc).WherePasses(amb_como_filtro).ToElements()    # Use filter to retrieve elements
    # lista_python_collected_elements = ['Ambiente {}: {}'.format(amb),list(collected_intersecting_elements)]
    forros_categ = str(DB.BuiltInCategory.OST_Ceilings)
    paredes_categ = str(DB.BuiltInCategory.OST_Walls)
    pisos_categ = str(DB.BuiltInCategory.OST_Floors)

    categorias_relevantes = [forros_categ, paredes_categ, pisos_categ]
    categorias_em_PTBR = ['Paredes', 'Pisos', 'Forros']
    funcoes = ['Finish2', 'Membrane']
    print('ENCONTRADOS os seguintes objetos:')

    for elem in elementos_intersectantes:
        # SEM O TRY/EXCEPT ELE NAO CONSEGUE ITERAR POR TODOS OS ELEMENTOS:
        try:
            # DEFINIÇÕES:
            categ = str(elem.Category.BuiltInCategory)

            if any(str(elem.Category.BuiltInCategory) == categoria for categoria in categorias_relevantes):
                # print('{}, {}, cód. ID {}'.format(elem.Name, elem.Category.Name, elem.Id))
                elem_type_id = elem.GetTypeId()
                elem_type = doc.GetElement(elem_type_id)
                elem_estrut = DB.HostObjAttributes.GetCompoundStructure(elem_type)
                camadas = elem_estrut.GetLayers()
                quant_camadas = elem_estrut.LayerCount
                # print(quant_camadas)
                for camada in camadas:
                    funcao = camada.Function.ToString()
                    # a lista de critérios (tewmporariamente) que atuarão como filtro
                    is_camada_acabamento_ou_membrana = any(str(camada.Function.ToString()) == funcao_correta for funcao_correta in funcoes)
                    is_camada_mais_externa = camada.LayerId == 0
                    is_camada_mais_interna = camada.LayerId == quant_camadas - 1
                    #essa condição abaixo não é ideal, é apenas temporária, pois foi necessário p/ que nao fosse incluido como material de revestimento
                    # o "granito polido" da divisoria dos wcs, no térreo do projeto piloto (CIn - Bloco E). A refinar condição para que seja
                    # aplicávle em outros casos/edificações na universidade
                    #esse 0.1 é em double, e não em cm. em cm é aprox 2 a 3cm
                    conditions = [
                        is_camada_mais_interna,
                        is_camada_acabamento_ou_membrana
                    ]
                    #and elem_type.Width > 0.05
                    # print('a camada superficial do ambiente {} é a index {}, {}'.format(amb_name, camada.LayerId, funcao))
                    mat_rev_camada = doc.GetElement(DB.ElementId(int(camada.MaterialId.ToString())))
                    marca = mat_rev_camada.get_Parameter(DB.BuiltInParameter.ALL_MODEL_MARK).AsString()

                    # mas provavelmente vai ser interessante passar em ao menos 2 desses criterios.
                    # funcoes_camada_filtro or camada.LayerId == quant_camadas - 1 or camada.LayerId == 0 and elem_type.Width > 0.1:
                    if categ == paredes_categ and is_camada_acabamento_ou_membrana:
                        # print(elem.Name, elem.Id)
                        mat_parede = mat_rev_camada
                        lista_mats_paredes.append(mat_parede.Id)
                    #                         print('material PAREDE em {}: {}'.format(amb_name, mat_parede.Name))
                    elif categ == forros_categ:
                        area_forro_str = elem.LookupParameter('Área').AsValueString()
                        area_forro = float((area_forro_str)[:5])
                        if amb_area * .9 < area_forro < amb_area * 1.1:
                            print('o forro do ambiente {} é: {}, {}, ID nº {}'.format(amb_name, elem.Name,
                                                                                      elem.Category.Name, elem.Id))
                            mat_forro = mat_rev_camada
                            t = DB.Transaction(doc, "aplicar cod revest forro a ambiente")
                            t.Start()
                            cod_forro.Set(mat_forro.Id)
                            t.Commit()

                    elif categ == pisos_categ: #and is_camada_mais_externa:
                        area_piso_str = elem.LookupParameter('Área').AsValueString()
                        area_piso = float((area_piso_str)[:5])
                        if amb_area * .85 < area_piso < amb_area * 1.2:
                            print('o piso do ambiente {} é: {}, {}, ID nº {}'.format(
                                amb_name, elem.Name, elem.Category.Name, elem.Id))
                            mat_piso = mat_rev_camada
                            print('material de piso identificado:', mat_piso.Name)

                            t = DB.Transaction(doc, "aplicar cod revest piso a ambiente")
                            t.Start()
                            cod_piso.Set(mat_piso.Id)
                            t.Commit()






                    # if any(condition == True for condition in conditions): #ok mas dessa forma é um OU (se satisfaz QUALQUER dos 4 critérios, ele "passa".
    #                     #mas provavelmente vai ser interessante passar em ao menos 2 desses criterios.
    #                     # funcoes_camada_filtro or camada.LayerId == quant_camadas - 1 or camada.LayerId == 0 and elem_type.Width > 0.1:
    #                     if categ == paredes_categ:
    #                         # print(elem.Name, elem.Id)
    #                         mat_parede = mat_rev_camada
    #                         lista_mats_paredes.append(mat_parede.Id)
    # #                         print('material PAREDE em {}: {}'.format(amb_name, mat_parede.Name))
    #                     elif categ == forros_categ:
    #                         area_forro_str = elem.LookupParameter('Área').AsValueString()
    #                         area_forro = float((area_forro_str)[:5])
    #                         if amb_area * .9 < area_forro < amb_area * 1.1:
    #                             print('o forro do ambiente {} é: {}, {}, ID nº {}'.format(amb_name,elem.Name,elem.Category.Name,elem.Id))
    #                             mat_forro = mat_rev_camada
    #                             t = DB.Transaction(doc, "aplicar cod revest forro a ambiente")
    #                             t.Start()
    #                             cod_forro.Set(mat_forro.Id)
    #                             t.Commit()
    #                     elif categ == pisos_categ and is_camada_mais_externa:
    #                         area_piso_str = elem.LookupParameter('Área').AsValueString()
    #                         area_piso = float((area_piso_str)[:5])
    #                         if amb_area * .85 < area_piso < amb_area * 1.2:
    #                             print('o piso do ambiente {} é: {}, {}, ID nº {}'.format(
    #                                 amb_name, elem.Name, elem.Category.Name, elem.Id))
    #                             mat_piso = mat_rev_camada
    #                             print('material de piso identificado:', mat_piso.Name)
    #
    #                             t = DB.Transaction(doc, "aplicar cod revest piso a ambiente")
    #                             t.Start()
    #                             cod_piso.Set(mat_piso.Id)
    #                             t.Commit()
        except AttributeError:
            pass
    lista_mats_paredes = list(set(lista_mats_paredes))
    if len(lista_mats_paredes) == 2:
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
    elif len(lista_mats_paredes) == 1:
        t3 = DB.Transaction(doc, "aplicar cods revest adicionais de parede ao ambiente")
        t3.Start()
        cod_paredes.Set(lista_mats_paredes[0])
        t3.Commit()



    # print(len(lista))
    # lista = list(set(lista))
    # print('Após remoção de duplicados, a quantidade de materiais de revestimento '
    #       'localizados no ambiente {} é {}'.format(amb_name, len(lista)))

# for material in materiais:
#     try:
#         if material.Id == lista[0]:
#             print(material.Name)
#             revparede1 = material.Id
#             t3 = DB.Transaction(doc, "aplicar cods revest adicionais de parede ao ambiente")
#             t3.Start()
#             cod_paredes.Set(revparede1)
#             t3.Commit()
#         elif material.Id == lista[1]:
#             print(material.Name)
#             revparede2 = material.Id
#             t4 = DB.Transaction(doc, "aplicar cods revest adicionais de parede ao ambiente")
#             t4.Start()
#             cod_paredes2.Set(revparede2)
#             t4.Commit()
#         elif material.Id == lista[2]:
#             print(material.Name)
#             t5 = DB.Transaction(doc, "aplicar cods revest adicionais de parede ao ambiente")
#             t5.Start()
#             cod_paredes3.Set(material.Id)
#             t5.Commit()
#     except IndexError:
#         pass


# t3 = DB.Transaction(doc, "aplicar cod revest parede a ambiente")
# t3.Start()
# cod_paredes2.Set((lista[1]).Id)
# cod_paredes3.Set((lista[2]).Id)
# t.Commit()

# isso abaixo são linhas iniciais pra caso queira levar a cabo a alternativa de fazer uma so transaction PRA APLICAr OS MATERIAIS coletados aos
#respectivos campos de parametro, mas porvavelmente vai ser melhor fazer uma transaction por tipo de elemento construtivo (piso,parede,forro)
# print(lista_final_materiais_por_ambiente
# for i in lista_final_materiais_por_ambiente:
#     t = DB.Transaction(doc, "aplicar cod revest parede a ambiente")
#     t.Start()
#     cod_paredes.Set(mat_rev_camada.Id)
#     t.Commit()