# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as revit

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

# tutorial parameteres:https://www.youtube.com/watch?v=YoLxucuC6Ss
#ATÉ O FIM, DEMONSTRAÇAO DE QUE É POSSIVEL ACESSAR INFORMAÇAO OU POR UM ID DE OBJETO
#JA CONHECIDO (wall_id) ou iterando por uma lista de objetos (all_walls)
all_walls = revit.FilteredElementCollector(doc).OfCategory(revit.BuiltInCategory.OST_Walls)

# for wall in all_walls:
#     print(wall.Id)
    # for p in wall.Parameters:
    #     # print(p.Definition.Name)
    #     wall_c = wall.get_Parameter(revit.BuiltInParameter.ALL_MODEL_TYPE_NAME)
    #     print(wall_c.AsString())
    # print(wall.Name) #nao funciona!! nao faz sentido pq Name é um mebro (DO TIPO eLEMENT) DA wALLtYPE

materiais = revit.FilteredElementCollector(doc).OfCategory(revit.BuiltInCategory.OST_Materials)
# for material in materiais:
#     print(material.Name)
#     print('O material se chama {} e está na categoria {}.'.format(material.Name, material.Category.Name))
    # print(material.IsValidObject)

wall_id = doc.GetElement(revit.ElementId(343830))
# print(list(wall_id.Parameters))
# for p in wall_id.Parameters:
    #     print('\n{}'.format(p.Definition.Name))
    #     print(p.Definition.BuiltInParameter)
    #     print(p.IsReadOnly)
    #     print(p.StorageType)

wall_c = wall_id.get_Parameter(revit.BuiltInParameter.ELEM_TYPE_PARAM)
print(wall_c.AsValueString()) #asvaluestring funciona, asstring nao funciona.

ambiente_hall = doc.GetElement(revit.ElementId(611306))
# print(ambiente_hall.LookUpParameter('COD-REVEST_PAREDES'))

#abaixo, ele encontrou o parametro compartilhado de revest de paredes no ambiente especificado.
for a in ambiente_hall.Parameters:
    id_param = a.Id
    # print(id_param)
    nome_param = a.Definition.Name
    if nome_param == 'COD-REVEST_PAREDES':
        print(nome_param)
        revest_parede = a
        #abaixo, acessei o valor atribuído ao parametro compartilhado COD-REVEST_PAREDES:
        print(a.AsValueString())
        for material in materiais:
            if material.Name == revest_parede.AsValueString():
                print('achou')


# rev_parede_hall = ambiente_hall.get_Parameter(revit.)



#print(wall_id.GetMaterialVolume(??))
# print(mats)
# for m in mats:
#     print(m.Definition.Name)

#FIM
#---------------------------------------------------------------------------


# area_tags = revit.FilteredElementCollector(doc).OfCategory(revit.BuiltInCategory.OST_AreaTags).ToElements()
# print(area_tags)
#
# all_furniture = revit.FilteredElementCollector(doc)
# all_furniture.OfCategory(revit.BuiltInCategory.OST_Furniture)
# all_furniture.WhereElementIsNotElementType()
# all_furniture.ToElements()
# print(all_furniture)
#
# type_name = doc.get_Parameter(revit.BuiltInParameter.OST_AreaTags).AsDouble()
# print(type_name)






# from pyrevit import DB, UI
# from pyrevit import forms
#
# forms.ask_for_string(
#     default='some-tag',
#     prompt='Enter new tag name:',
#     title='Tag'
# )
# forms.
# DB.