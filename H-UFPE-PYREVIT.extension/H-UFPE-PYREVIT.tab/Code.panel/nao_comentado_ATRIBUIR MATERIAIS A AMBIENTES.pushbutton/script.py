# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as revit
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

materiais = revit.FilteredElementCollector(doc).OfCategory(revit.BuiltInCategory.OST_Materials).ToElements()
ambientes = revit.FilteredElementCollector(doc).OfCategory(revit.BuiltInCategory.OST_Rooms).ToElements()
all_walls = revit.FilteredElementCollector(doc).OfCategory(revit.BuiltInCategory.OST_Walls).WhereElementIsNotElementType()
all_walls_list = all_walls.ToElements()
tipos_parede =  revit.FilteredElementCollector(doc).OfCategory(revit.BuiltInCategory.OST_Walls).WhereElementIsElementType().ToElements()
    # parede.CompoundStructure.GetLayers()
for walltype in tipos_parede:
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
            if camada.Function.ToString() == 'Finish2' and camada.LayerId == 4:
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

# for walltype in tipos_parede:
#     id = walltype.Id
#     titulo_tipo = walltype.get_Parameter(revit.BuiltInParameter.ALL_MODEL_TYPE_NAME)
#     print(titulo_tipo.AsString())

# revestimentos_coletados = [material.Name for material in materiais if material.Id == id_material_camada]
