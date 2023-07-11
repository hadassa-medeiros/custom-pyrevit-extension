# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

materiais_collector = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Materials)
ambientes_collector = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms)
paredes_collector =   DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls)
pisos_collector =     DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Floors)
forros_collector =    DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Ceilings)

materiais = materiais_collector.ToElements()
ambientes = ambientes_collector.ToElements()
pisos = pisos_collector.ToElements()
forros = forros_collector.ToElements()
paredes = paredes_collector.ToElements()
paredes_instancias = paredes_collector.WhereElementIsNotElementType().ToElements()
todos_elem_constr = [pisos_collector, forros_collector, paredes_collector]
ambientes_em_teste = []
# ids = [1123256, 1123259, 1123262, 1502389, 618033, 1123955, 1123958]
ids = [1123955] #copa mezanino

for id in ids:
    amb = doc.GetElement(DB.ElementId(id))
    ambientes_em_teste.append(amb)
print('Localizadas XYZ bounding box dos seguintes elementos:')

for ambiente in ambientes_em_teste:
    ambiente_level = ambiente.Level.Name
    ambiente_id = ambiente.Id.ToString()
    ambiente_name = ambiente.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
    ambiente_elem = doc.GetElement(DB.ElementId(int(ambiente_id)))
    ambiente_bbox = ambiente.get_BoundingBox(doc.ActiveView)
#_______________________________________________________________________
    # #transofrmar o type XYZ tanto do min como do max da boundingbox do ambiente,
    # # pra conseguir aplicar fator, pra deixar os limites do ambiente "menores",
    # # na intenção de que o filtro de elem intersectantes não "colete" elem construtivos
    # # de ambientex adjacentes àquele do qual se desej aobter os revestimentos.
    # #porx ex: ele nao retornaria mais o forro do ambiente hall no mezanino, apenas por ele
    # # estar bem próximo ao limite do ambiente Copa.
    # min0 = float(ambiente_bbox.Min[0]) #10.726396151
    # min1 = float(ambiente_bbox.Min[1]) # -89.358506603
    # min2 = float(ambiente_bbox.Min[2]) #11.975065617
    # max0 = float((ambiente_bbox.Max[0])) # 26.441619248
    # max1 = float((ambiente_bbox.Max[1]) * 1.3) # -72.964331803
    # max2 = float((ambiente_bbox.Max[2]) * 1.1)  # 18.536745407

    # pos_conversao_ambiente_bbox_MIN = DB.XYZ(min0,min1,min2)
    # pos_conversao_ambiente_bbox_MAX = DB.XYZ(max0, max1, max2)
    ambiente_outline = DB.Outline(ambiente_bbox.Min,ambiente_bbox.Max)  # é a outline que se passa como arg pro método DB.BoundingBoxIntersectsFilter (e não um objeto tipo BoundingBoxXYZ
    # ambiente_outline = DB.Outline(pos_conversao_ambiente_bbox_MIN, ambiente_bbox.Max) #é a outline que se passa como arg pro método DB.BoundingBoxIntersectsFilter (e não um objeto tipo BoundingBoxXYZ
    # ambiente_outline = DB.Outline(ambiente_bbox.Min, pos_conversao_ambiente_bbox_MAX) #é a outline que se passa como arg pro método DB.BoundingBoxIntersectsFilter (e não um objeto tipo BoundingBoxXYZ
#_______________________________________________________________________

    cod_paredes = ambiente.LookupParameter('COD-REVEST_PAREDES')
    cod_paredes2 = ambiente.LookupParameter('COD-REVEST2_PAREDES')
    cod_piso = ambiente.LookupParameter('COD-REVEST_PISO')
    cod_teto = ambiente.LookupParameter('COD-REVEST_TETO')
    print('{} - {}'.format(ambiente_name, ambiente_level))

    ambiente_como_filtro = DB.BoundingBoxIntersectsFilter(ambiente_outline)# Create filter
    intersecting_elements = DB.FilteredElementCollector(doc).WherePasses(ambiente_como_filtro).ToElements()    # Use filter to retrieve elements
    # lista_python_collected_elements = ['Ambiente {}: {}'.format(ambiente),list(collected_intersecting_elements)]
    categorias_em_PTBR = ['Paredes', 'Pisos', 'Forros']
    categorias_relevantes = [
        str(DB.BuiltInCategory.OST_Ceilings),
        str(DB.BuiltInCategory.OST_Walls),
        str(DB.BuiltInCategory.OST_Floors)
    ]
    cont_elem = 0
    print('ENCONTRADOS os seguintes objetos:')

    for element in intersecting_elements:
        #inserir aqui regra de q p o elemento contar, deve passar por um 2o filtro, o de se for forro ou piso, "pertencer àquele ambiente. é possível? pq
        # ta dificl adivinhar atraves dos valores das coordenadas qual seria um valor ideal p deixar de for aos elementos de ambiente adjacentes.

        try:
            if any(str(element.Category.BuiltInCategory) == categoria for categoria in categorias_relevantes):
                print('{}, {}, cód. ID {}'.format(element.Name, element.Category.Name, element.Id))
                cont_elem += 1
                element_type_id = element.GetTypeId()
                element_type = doc.GetElement(element_type_id)
                estrut_element = DB.HostObjAttributes.GetCompoundStructure(element_type)
                quant_camadas = estrut_element.LayerCount
                camadas_estrut = estrut_element.GetLayers()
                print(element_type.Name)
                for camada in camadas_estrut:
                    funcao = camada.Function.ToString()
                    if funcao == 'Finish2' or funcao == 'Membrane':
                        try:
                            if element.Category.Name == 'Paredes':
                                # acessar objeto dentre lista Materiais a partir do id do mat. atribuído à camada de revestimento Finish2
                                material_rev_parede = doc.GetElement(DB.ElementId(int(camada.MaterialId.ToString())))
                                print(material_rev_parede.Name, element.Name)
                                for material in materiais:
                                    if material.Id == camada.MaterialId:
                                        revest_parede = material
                                        # print('ok, material associado a PAREDE:', revest_parede.Name)
                                t = DB.Transaction(doc, "aplicar cod revest a ambiente")
                                t.Start()
                                cod_paredes.Set(revest_parede.Id)
                                t.Commit()
                            elif element.Category.Name == 'Pisos':
                                material_rev_piso = doc.GetElement(DB.ElementId(int(camada.MaterialId.ToString())))
                                print(material_rev_piso.Name, element.Name)
                                for material in materiais:
                                    if material.Id == camada.MaterialId:
                                        revest_piso = material
                                        print('ok, material associado a PISO:', revest_piso.Name)
                                t = DB.Transaction(doc, "aplicar cod revest a ambiente")
                                t.Start()
                                cod_piso.Set(revest_piso.Id)
                                t.Commit()
                            elif element.Category.Name == 'Forros':
                                material_rev_forro = doc.GetElement(DB.ElementId(int(camada.MaterialId.ToString())))
                                print(material_rev_forro.Name, element.Name)
                                for material in materiais:
                                    if material.Id == camada.MaterialId:
                                        revest_forro = material
                                        print('ok, material associado a FORRO:', revest_forro.Name)
                                t = DB.Transaction(doc, "aplicar cod revest forro a ambiente")
                                t.Start()
                                cod_teto.Set(revest_forro.Id)
                                t.Commit()

                        except AttributeError as e:
                            print('erro ao tentar printar nome do objeto:', camada.Id, e)
                    # elif camada.Function.ToString() == 'Membrane' or camada.LayerId == quant_camadas - 1:
                    # elif element.Category.Name == 'Forros' and camada.LayerId == quant_camadas - 1:
                    #     print('element.Category.Name')
                    #     material_rev_forro = doc.GetElement(DB.ElementId(int(camada.MaterialId.ToString())))
                    #     print(material_rev_forro.Name, element.Name)
                    #     for material in materiais:
                    #         if material.Id == camada.MaterialId:
                    #             revest_forro = material
                    #             print('ok, material associado a FORRO:', revest_forro.Name)
                    #     t = DB.Transaction(doc, "aplicar cod revest forro a ambiente")
                    #     t.Start()
                    #     cod_teto.Set(revest_forro.Id)
                    #     t.Commit()
        except AttributeError:
            pass











# SINTAXES QUE FUNCIONARAM:
 # pra retornar nome (string) de tipo de objeto (ex: nome do tipo da parede tal)
# for wall_instancia in all_walls_list:
#     titulo = wall_instancia.get_Parameter(DB.BuiltInParameter.ELEM_TYPE_PARAM)
#     print(titulo.AsValueString())

# for parede_tipo in paredes_tipos:
#     id = parede_tipo.Id
#     titulo_tipo = parede_tipo.get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_NAME)
#     print(titulo_tipo.AsString())

# revestimentos_coletados = [material.Name for material in materiais if material.Id == id_material_camada]
