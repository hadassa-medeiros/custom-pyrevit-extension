# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as rvt

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

# all_walls = rvt.FilteredElementCollector(doc).OfCategory(rvt.BuiltInCategory.OST_Walls)
# all_walls = rvt.FilteredElementCollector(doc).OfCategory(rvt.BuiltInCategory.OST_HostFinWall)
#
# for wall in all_walls:
#     if wall.IsInRoom == True:
#         print(door.ID)

pisos = rvt.FilteredElementCollector(doc).OfCategory(rvt.BuiltInCategory.OST_Floors)
materiais = rvt.FilteredElementCollector(doc).OfCategory(rvt.BuiltInCategory.OST_Materials)
# met = rvt.FilteredElementCollector(doc).WherePasses(GetType('floor'))

# paredes = rvt.FilteredElementCollector(doc).OfCategory(rvt.BuiltInCategory.OST_Walls)
# forros = ...nao consegui pelo OST_Ceilings

#---------------------------------------
# ABAIXO, .Name nao funciona nem pra os objetos de piso dentro do collector Pisos nem pra paredes. so funciona pra Material. por quê?

# lista_pisos = [str(piso.Name) for piso in pisos]
# lista_paredes = [str(parede.Name) for parede in paredes] #dando prob com caracteres com acento, descobrir como fazer os materiais serem escritos correto na lista
lista_materiais = [str(material.Name) for material in materiais] #dando prob com caracteres com acento, descobrir como fazer os materiais serem escritos correto na lista
print(len(lista_materiais)) #funciona
print(lista_materiais)
#--------------------------------------------------

for piso in pisos:
    print(piso.GetMaterialIds)
    print(piso.GetType())
    print(piso.)
    # revest = rvt.Element.GetMaterialIds(piso, pisos)
    # a = piso.GetMaterialIds(pisos)  NAO FUNCIONA.

# for parede in paredes:
#     print('A parede está na categoria {}.'.format(parede.Category.Name))



for material in materiais:
    print(material.Name)
    print('O material se chama {} e está na categoria {}.'.format(material.Name, material.Category.Name))
    print(material.IsValidObject)
#ISSO FUNCIONOU!!!!!!!
    # em vez de mostrar '<Autodesk.Revit.DB.Category object at 0x0000000000009343 [Autodesk.Revit.DB.Category]>' mostrou 'Materiais'

# print('A contagem total neste projeto é: {} pisos, {} paredes, {} materiais.'.format(cont_pisos, cont_paredes, cont_materiais))






# #trying to acces the parameter room_name of some random room:
# room1_id = rvt.ElementId(1123259)  #Ambiente WC M. - 1 PAVTO
# room2_id = rvt.ElementId(611306) #Ambiente HALL - 1 PAVTO
# # Get the room element from the ElementId
# # room1 = doc.GetElement(room1_id)
# # room2 = doc.GetElement(room2_id)
#
# #now, testing how to get information from multiple elements inside the project(proper loops and methods to be used
# # as nexts steps):
# list_of_rooms_by_id = [room1_id, room2_id]
# for id in list_of_rooms_by_id:
#     room = doc.GetElement(id)
#     param_set = room.Parameters.Size
#     print('{} has {} parameters inside it.'.format(room,param_set))
#     print(room.Area/10.764)
#     print(room.CanBeHidden) # with this synthax being used, it doesn't return TRUE or FALSE despite being boolean.
#     #what then woul di write to retrieve a True for the CanBeHidden method? https://www.revitapidocs.com/2015/887010c4-de58-96b6-0931-4c226e6b142b.htm
#     print(room.Level.Name)


# room_name_param = parameter_set[rvt.BuiltInParameter.ROOM_NAME]
# print(room_name_param)


# FUNCIONA mas sem utilidade por ora pois nao pretendo "chamar' elementos pelos seu IDs e sim por human readable language
# e_id        = rvt.ElementId(2219611)
# element = doc.GetElement(e_id)

# is_it_in_room = element.IsInRoom
# print(is_it_in_room, element)


#GET INFO
# e_cat       = element.Category
# e_level_id  = element.LevelId
# e_wall_type = element.WallType
