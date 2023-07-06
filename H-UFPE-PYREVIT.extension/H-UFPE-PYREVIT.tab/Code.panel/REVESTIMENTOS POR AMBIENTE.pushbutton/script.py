# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as revit

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

materiais_collector = revit.FilteredElementCollector(doc).OfCategory(revit.BuiltInCategory.OST_Materials)
ambientes_collector = revit.FilteredElementCollector(doc).OfCategory(revit.BuiltInCategory.OST_Rooms)
paredes_collector =   revit.FilteredElementCollector(doc).OfCategory(revit.BuiltInCategory.OST_Walls)
pisos_collector =     revit.FilteredElementCollector(doc).OfCategory(revit.BuiltInCategory.OST_Floors)
forros_collector =    revit.FilteredElementCollector(doc).OfCategory(revit.BuiltInCategory.OST_Ceilings)

materiais = materiais_collector.ToElements()
ambientes = ambientes_collector.ToElements()
pisos =     pisos_collector.ToElements()
forros =    forros_collector.ToElements()
paredes =   paredes_collector.ToElements()
paredes_instancias = paredes_collector.WhereElementIsNotElementType().ToElements()
todos_elem_constr = [pisos_collector, forros_collector, paredes_collector]



amb_lavabo =  doc.GetElement(revit.ElementId(1123256))
amb_wcm = doc.GetElement(revit.ElementId(1123259))
amb_wcf = doc.GetElement(revit.ElementId(1123262))
ambientes_em_teste = [amb_wcm]
# nome = amb_wcm.Name.Value #DUVIDA: não entendi pq o atributo Name nao pega aqui mas pegou p ver o nome da parede.
print('Localizadas coordenadas XYZ da bounding box dos seguintes elementos:')
for ambiente in ambientes_em_teste:
    ambiente_id = ambiente.Id.ToString()
    ambiente_name = ambiente.get_Parameter(revit.BuiltInParameter.ROOM_NAME).AsString()
    ambiente_level = ambiente.Level.Name
    ambiente_elem = doc.GetElement(revit.ElementId(int(ambiente_id)))
    ambiente_bbox = ambiente.get_BoundingBox(doc.ActiveView)
    ambiente_outline = revit.Outline(ambiente_bbox.Min, ambiente_bbox.Max) #é a outline que se passa como arg pro método revit.BoundingBoxIntersectsFilter (e não um objeto tipo BoundingBoxXYZ
    cod_paredes = ambiente.LookupParameter('COD-REVEST_PAREDES')
    cod_piso = ambiente.LookupParameter('COD-REVEST_PISO')
    cod_teto = ambiente.LookupParameter('COD-REVEST_TETO')
    print('{} - {}'.format(ambiente_name, ambiente_level))

    ambiente_como_filtro = revit.BoundingBoxIntersectsFilter(ambiente_outline)# Create filter
    intersecting_elements = revit.FilteredElementCollector(doc).WherePasses(ambiente_como_filtro).ToElements()    # Use filter to retrieve elements
    # lista_python_collected_elements = ['Ambiente {}: {}'.format(ambiente),list(collected_intersecting_elements)]
    # Iterate over the elements
    categorias_em_PTBR = ['Paredes', 'Pisos', 'Forros']
    categorias_relevantes = [
        str(revit.BuiltInCategory.OST_Floors),
        str(revit.BuiltInCategory.OST_Walls),
        str(revit.BuiltInCategory.OST_Ceilings)
    ]
    cont_elem = 0
    print('ENCONTRADOS os seguintes objetos:\n\n')
    for element in intersecting_elements:
        # print(element.get_Parameter(revit.BuiltInParameter.ELEM_CATEGORY_PARAM).AsValueString())
        try:
            if any(str(element.Category.BuiltInCategory) == categoria for categoria in categorias_relevantes):
                print('{}, {}, cód. ID {}'.format(element.Name, element.Category.Name, element.Id))
                cont_elem += 1
                element_type_id = element.GetTypeId()
                element_type = doc.GetElement(element_type_id)
                estrut_element = revit.HostObjAttributes.GetCompoundStructure(element_type)
                quant_camadas_estrut = estrut_element.LayerCount
                camadas_estrut = estrut_element.GetLayers()
                for camada in camadas_estrut:
                    try:
                        # caso de pisos:
                        if camada.Function.ToString() == 'Finish2' and element.Category.Name == 'Paredes':  # uma forma de double check: tanto q a camada da parede é de fato de revestimento tipo Acabamento2 (a última na hierarquia),
                            id_mat_revest_piso = int(camada.MaterialId.ToString())
                            # acessar objeto type Material dentre lista Materiais projeto a partir do id mat. atribuído à camada de revestimento Finish2 interna
                            material_pelo_id_revest_piso = doc.GetElement(revit.ElementId(id_mat_revest_piso))
                            print('aqui')
                            print(material_pelo_id_revest_piso.Name, element.Name)
                            for material in materiais:
                                if material.Id == camada.MaterialId:
                                    revest = material
                                    print('ok, material associado a parede:',revest.Name)
                    #caso de forros e paredes:
                        elif camada.Function.ToString() == 'Finish2' and camada.LayerId == quant_camadas_estrut-1:
                        #ou: (posso deixar mais explicito que to aplicando a piso forro e parede na condicao chamada em vez de usar a regra sobre hierarquia/index das camadas
                        # elif camada.Function.ToString() == 'Finish2' and element.Category.Name == 'Piso' ou forro
                            print('acima deve retornar só ou forro ou parede')

                    except AttributeError as e:
                        print('erro ao tentar printar nome do objeto:', piso.Id, e)
        except AttributeError as e:
            # print('-'*50,element.Name,e)
            pass
            # print('TOTAL: {} elementos construtivos de interesse em {}{}'.format(cont_elem, ambiente_name, '-'*50))
            # print('\n')
            # COLETA/IDENTIFICA MATERIAIS DAS CAMADAS DE REVESTIMENTO DE PISOS
  # AQUI VAI SER O CODIGO COMPLETO, COM UM ITERADOR Q DENTRO DELE CONTEM OS 3 CASOS:PISO/FOORO/PAREDE E NO FIM ATRIBUI O COD POR UMA TRANSACTION.

# # t = revit.Transaction(doc, "aplicar cod revest a ambiente")
# # t.Start()
# # cod_paredes.Set(material_teste_ID)
# # t.Commit()


for parede_tipo in paredes_collector.WhereElementIsElementType():
    nome_tipo = parede_tipo.get_Parameter(revit.BuiltInParameter.ALL_MODEL_TYPE_NAME)
    if nome_tipo.AsString() != 'Parede cortina':
        estrutura_parede = revit.HostObjAttributes.GetCompoundStructure(parede_tipo)
        quant_camadas_parede = estrutura_parede.LayerCount
        print(quant_camadas_parede)
        camadas_estrutura_parede = estrutura_parede.GetLayers()
        for camada in camadas_estrutura_parede:
            funcao_camada = camada.Function
            # print(type(funcao_camada)) # o tipo aqui é 'MaterialFunctionAssignment', nativo Revit API
            funcao_camada_str = funcao_camada.ToString() #pro tipo da variável virar string obviamente
            if camada.Function.ToString() == 'Finish2' and camada.LayerId == estrutura_parede.LayerCount-1: #uma forma de double check: tanto q a camada da parede é de fato de revestimento tipo Acabamento2 (a última na hierarquia),
                #como que se trata da camada mais interna da parede, que faceia o ambiente interno que ela delimita.(
                id_revest = int(camada.MaterialId.ToString())
            # acessar objeto Material (type Material contendo todas as infos)
            # dentre a lista completa de Materiais no projeto a partir do id do mat. atribuído à camada
                # de revestimento Finish2 interna
                material_teste = doc.GetElement(revit.ElementId(id_revest))
                print(material_teste.Name)
            # for material in materiais:
            #     if material.Id == camada.MaterialId:
            #     revest = material
            #     print(material.Name)
        # print(revestimentos_coletados)


#
# material_teste = doc.GetElement(revit.ElementId(414))
# material_teste_ID = material_teste.Id
# nome_material_teste_NOME = material_teste.Name
# material_teste_MARCA = material_teste.get_Parameter(revit.BuiltInParameter.ALL_MODEL_MARK)
# materiais_em_parede_testando = parede_testando.GetMaterialIds(False)
# print(materiais_em_parede_testando)
# for id_material_parede in materiais_em_parede_testando:
#     print(id_material_parede)
#     for material in materiais:
#         cod_mat_parede_str = material.get_Parameter(revit.BuiltInParameter.ALL_MODEL_MARK).AsValueString()
#         print(cod_mat_parede_str)
        # print(material.Name)
        # if material.Id == id_material_parede:
        #     print('encontrado:',material.Name)
        #     # mat_parede = material
        #     cod_mat_parede = material.get_Parameter(revit.BuiltInParameter.ALL_MODEL_MARK)
        #     cod_mat_parede_str = material.get_Parameter(revit.BuiltInParameter.ALL_MODEL_MARK).AsValueString()
        #     print(cod_mat_parede_str) #LOCALIZEI AQUI O CÓDIGO ESCRITO NO CAMPO NATIVO 'MARCA',DENTRO
        #     # DE CADA MATERIAL.

# camadas = doc.GetElement(revit.ElementId(1977638)).CompoundStructure
# print(list(camadas.GetLayers()))

#     PRA O LOOKUP FUNCIONAR NESSE CASO ONDE ELE ITERA POR TODAS, VOU TER QUE USAR ERROR HANDLING PRA
#     QUANDO ELE SE DEPARAR COM PAREDES QUE POR ALGUMA RAZÃO TENHAM VALOR NULO NESSE PARAMETRO 'ÁREA'
#     OU ERROR HANDLING (IMAGINO QUE SEJA A FORMA MAIS ELEGANTE/EM CONFOMRIDADE COM BOAS PRÁTICAS) OU
#     CRIAR UM IF/CONDIÇAO P Q ELE SO ACESSE/PRINTE O PARAMETRO ÁREA DAS PAREDES Q TENHAM ESSE PARAMETRO, NE
#     print(area_parede.AsValueString())
#     print(wall.Id)
#     for p in wall.Parameters:
#         # print(p.Definition.Name)
#         wall_c = wall.get_Parameter(revit.BuiltInParameter.ALL_MODEL_TYPE_NAME)
#         print(wall_c.AsString())
#     print(wall.Name) #nao funciona!! nao faz sentido pq Name é um mebro (DO TIPO eLEMENT) DA parede_tipo
#


# print(list(wall_id.Parameters))
# for p in wall_id.Parameters:
#         print('\n{}'.format(p.Definition.Name))
#
# ambiente_hall = doc.GetElement(revit.ElementId(611306))
# #abaixo, ele encontrou o parametro compartilhado de revest de paredes no ambiente especificado.
# for parametro in ambiente_hall.Parameters:
#     id_param = parametro.Id
#     print(id_param)
#     nome_param = parametro.Definition.Name
#     print(nome_param)
#     if nome_param == 'COD-REVEST_PAREDES':
#         revest_parede = parametro
#         print('aqui,{}'.format(revest_parede.AsValueString()))
#         #abaixo, acessei o valor atribuído ao parametro compartilhado COD-REVEST_PAREDES:
#         print(parametro.AsValueString())
#         for material in materiais:
#             if material.Name == revest_parede.AsValueString():
#                 print('achou') #ele identificou aqui dentre todos os materiais presentes no projeto,
#                 #armazenados na variavel materiais, aquele encontrado no objeto ambiente_hall.


# SINTAXES QUE FUNCIONARAM:
 # pra retornar nome (string) de tipo de objeto (ex: nome do tipo da parede tal)
# for wall_instancia in all_walls_list:
#     titulo = wall_instancia.get_Parameter(revit.BuiltInParameter.ELEM_TYPE_PARAM)
#     print(titulo.AsValueString())

# for parede_tipo in paredes_tipos:
#     id = parede_tipo.Id
#     titulo_tipo = parede_tipo.get_Parameter(revit.BuiltInParameter.ALL_MODEL_TYPE_NAME)
#     print(titulo_tipo.AsString())

# revestimentos_coletados = [material.Name for material in materiais if material.Id == id_material_camada]
