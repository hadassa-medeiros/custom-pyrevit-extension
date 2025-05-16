# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from revit_doc_interface import (
    RevitDocInterface,
    get_name,
    get_room_number,
    double_to_metric,
    sq_ft_to_m2,
    get_elem_from_typeId,
    get_room_area
)
import Autodesk.Revit.UI.Selection as sel
from pyrevit import forms

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application
interface = RevitDocInterface()

__title__ = "Área de Soleiras"
__annotations__ = "Recalcula área do ambiente adicionando a soma das áreas de soleira das portas que se originam dele"
__doc__ = "Recalcula áreas de ambientes adicionando a soma das áreas de soleiras de portas cujo ambiente de origem é o ambiente em questão"
__author__ = "Hadassa Medeiros"

# encontrar e armazenar objeto phase cujo nome seja "LEVANTAMENTO"
phase = interface.find_phase_by_name("LEVANTAMENTO")
# acessar todas as portas do projeto
all_doors = interface.doors
regular_doors = [door for door in all_doors if not door.Host or "Curtain" not in door.Host.Category.Name]

room_areas = {}
door_areas = {}
door_area_by_room = {

}

# o calculo so faz sentido para portas que conectam 2 ambientes (excluem-se portas internas a sanitarios, por exemplo):
def door_connects_different_rooms(door, phase):
    """
    Check if a door connects two different rooms in the specified phase.
    """
    try:
    # Get the 'FromRoom' and 'ToRoom' elements of the door
        origin_room = door.get_FromRoom(phase)
        destination_room = door.get_ToRoom(phase)

        # Check if both rooms are not None and are different
        if origin_room and destination_room and origin_room.Id != destination_room.Id:
            return True
        return False
    except Exception as e:
        print(e)
        pass

def calc_area_ambientes_com_soleira(door_list, room_num):
    # room_num = get_room_number(room)
    soleiras_ambiente = {room_num: []}
    for door in door_list:
        # print(door_connects_different_rooms(door, phase))
        door_type = doc.GetElement(door.GetTypeId())
        type_name = door_type.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        # print(type_name)        
        
        is_curtain = door.Host.Category.Id.IntegerValue == int(DB.BuiltInCategory.OST_CurtainWallPanels)
        # print(is_curtain)  
        if door_connects_different_rooms(door, phase) and get_room_number(door.get_FromRoom(phase)) == room_num:
            try:
                origin_room = door.get_FromRoom(phase)
                room_num = get_room_number(origin_room)

                print(room_num, " - ", get_name(origin_room))
                door_width = get_elem_from_typeId(door).get_Parameter(
                    DB.BuiltInParameter.DOOR_WIDTH
                    ).AsDouble()
                host_wall_type = doc.GetElement(door.Host.GetTypeId())
                host_wall_width = host_wall_type.GetCompoundStructure().GetWidth()
                
                area_soleira = door_width * host_wall_width
                area_soleira_m2 = sq_ft_to_m2(area_soleira)

                # # caso queira gerar memoria de calculo:
                memoria_calc_area_soleiras_m2 = "CALCULO: ", double_to_metric(door_width), " x ", double_to_metric(host_wall_width), "=", area_soleira
                # print(memoria_calc_area_soleiras_m2)

                # print(area_soleira_m2)
                soleiras_ambiente[room_num].append(area_soleira)

                contagem_soleiras_ambiente = len(soleiras_ambiente[room_num])
                area_soleiras_ambiente = sum(soleiras_ambiente[room_num])

                new_room_area = get_room_area(origin_room) + area_soleiras_ambiente
                param_area_ambiente_com_soleiras = origin_room.LookupParameter("ÁREA AMBIENTE C/ SOLEIRAS")
                param_area_soleiras = origin_room.LookupParameter("ÁREA TOTAL DE SOLEIRAS")
                param_contagem_soleiras = origin_room.LookupParameter("CONTAGEM SOLEIRAS")
                # memoria_calc_area_soleiras = origin_room.LookupParameter("MEMÓRIA CALCULO ÁREA SOLEIRAS")

                t = DB.Transaction(doc, "Registrar areas soleiras no respectivo ambiente")
                t.Start()
                param_area_soleiras.Set(area_soleiras_ambiente)
                param_area_ambiente_com_soleiras.Set(new_room_area)
                param_contagem_soleiras.Set(contagem_soleiras_ambiente)
                t.Commit()
            except Exception as e:
                print(e)
                pass
calc_area_ambientes_com_soleira(all_doors, "25")
# calc_area_ambientes_com_soleira(all_doors, "02")
# calc_area_ambientes_com_soleira(all_doors, "03")
# calc_area_ambientes_com_soleira(all_doors, "04")
# calc_area_ambientes_com_soleira(all_doors, "05")
# calc_area_ambientes_com_soleira(all_doors, "06")
# calc_area_ambientes_com_soleira(all_doors, "07")
# calc_area_ambientes_com_soleira(all_doors, "08")
# calc_area_ambientes_com_soleira(all_doors, "09")
# calc_area_ambientes_com_soleira(all_doors, "10")
# calc_area_ambientes_com_soleira(all_doors, "11")
# calc_area_ambientes_com_soleira(all_doors, "12")
# calc_area_ambientes_com_soleira(regular_doors, "18")


# for room in interface.rooms:
#     calc_area_ambientes_com_soleira(regular_doors, get_room_number(room))


# # coletar o parametro fromRoom de cada porta

# # relacionar cada ambiente do projeto com as portas que se originam dele
# # descobrir a area da soleira de cada porta e armazenar em um dicionário
# # somar a area das soleiras e associar ao ambiente via dois parametros compartilhados: area soleiras e area corrigida do ambiente (area original + area soleiras)
# # criar um arquivo CSV com os dados coletados: a area final de cada ambiente deve ser a area ROOM_AREA + a soma das areas de soleira de cada porta da qual
