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
paredes_tipos =  paredes_collector.WhereElementIsElementType().ToElements()

colecao_completa = [materiais, ambientes, pisos, forros, paredes]
colecao_obj_por_ambiente = []  # make this be a dict instead of list.

wall_a_partir_de_id = doc.GetElement(revit.ElementId(343830))
bbox_wall = wall_a_partir_de_id.get_BoundingBox(doc.ActiveView)
outline = revit.Outline(bbox_wall.Min, bbox_wall.Max) #é a outline que se passa como arg pro método revit.BoundingBoxIntersectsFilter (e não um objeto tipo BoundingBoxXYZ
print('As coordenadas XYZ da bounding box do elemento ID {} (categoria {}) foram localizadas.'.format(wall_a_partir_de_id.Id, wall_a_partir_de_id.Category.Name))

ambientes_em_teste = []
amb_lavabo =  doc.GetElement(revit.ElementId(1123256))
amb_wcm = doc.GetElement(revit.ElementId(1123259))
amb_wcf = doc.GetElement(revit.ElementId(1123262))

# nome = amb_wcm.Name.Value #DUVIDA: não entendi pq o atributo Name nao pega aqui mas pegou p ver o nome da parede.

print('Localizadas coordenadas XYZ da bounding box dos seguintes elementos:')
for ambiente in ambientes:
    ambiente_id = ambiente.Id.ToString()
    ambiente_name = ambiente.get_Parameter(revit.BuiltInParameter.ROOM_NAME).AsString()
    ambiente_level = ambiente.Level.Name
    ambiente_elem = doc.GetElement(revit.ElementId(int(ambiente_id)))
    ambiente_bbox = ambiente.get_BoundingBox(doc.ActiveView)
    ambiente_outline = revit.Outline(ambiente_bbox.Min, ambiente_bbox.Max) #é a outline que se passa como arg pro método revit.BoundingBoxIntersectsFilter (e não um objeto tipo BoundingBoxXYZ
    print('{} - {}'.format(ambiente_name, ambiente_level))
# Create filter
    ambiente_como_filtro = revit.BoundingBoxIntersectsFilter(ambiente_outline)
    # Use filter to retrieve elements
    collected_intersecting_elements = revit.FilteredElementCollector(doc).WherePasses(ambiente_como_filtro).ToElements()
    # lista_python_collected_elements = ['Ambiente {}: {}'.format(ambiente),list(collected_intersecting_elements)]
    colecao_obj_por_ambiente.append(collected_intersecting_elements)
# Iterate over the elements
    categorias_interessam = ['Paredes', 'Pisos', 'Forros']
    cont_elem = 0
    print('ENCONTRADOS os seguintes objetos:\n\n')
    for element in collected_intersecting_elements:     # Do something with the filtered elements
        try:
            if any(superficie == element.Category.Name for superficie in categorias_interessam):
                print('{}, {}, cód. ID {}'.format(element.Name, element.Category.Name, element.Id))
                cont_elem+=1
        except AttributeError as e:
            # print('-'*50,element.Name,e)
            pass
    print('TOTAL: {} elementos construtivos de interesse em {}{}'.format(cont_elem, ambiente_name, '-'*50))
    print('\n')

for walltype in paredes_tipos:
    wall_id = walltype.Id
    nome_tipo = walltype.get_Parameter(revit.BuiltInParameter.ALL_MODEL_TYPE_NAME)
    # print(titulo_tipo.AsString())
    if nome_tipo.AsString() != 'Parede cortina':
        estrutura_parede = revit.HostObjAttributes.GetCompoundStructure(walltype)
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
            # material_teste_ID = material_teste.Id
            # nome_material_teste_NOME = material_teste.Name
            # for material in materiais:
            #     if material.Id == camada.MaterialId:
            #     revest = material
            #     print(material.Name)
        # print(revestimentos_coletados)


# ambiente_testando = doc.GetElement(revit.ElementId(611306))
# parede_testando = doc.GetElement(revit.ElementId(358513))
#
# CODREVEST_PAREDES = ambiente_testando.LookupParameter('COD-REVEST_PAREDES')
# material_teste = doc.GetElement(revit.ElementId(414))
# material_teste_ID = material_teste.Id
# nome_material_teste_NOME = material_teste.Name
# material_teste_MARCA = material_teste.get_Parameter(revit.BuiltInParameter.ALL_MODEL_MARK)
# print(material_teste_MARCA)
# # t = revit.Transaction(doc, "aplicar cod revest a ambiente")
# # t.Start()
# # CODREVEST_PAREDES.Set(material_teste_ID)
# # t.Commit()
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
#     print(wall.Name) #nao funciona!! nao faz sentido pq Name é um mebro (DO TIPO eLEMENT) DA wALLtYPE
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

# for walltype in paredes_tipos:
#     id = walltype.Id
#     titulo_tipo = walltype.get_Parameter(revit.BuiltInParameter.ALL_MODEL_TYPE_NAME)
#     print(titulo_tipo.AsString())

# revestimentos_coletados = [material.Name for material in materiais if material.Id == id_material_camada]
