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
        destination_room = door.get_ToRoom(phase) if door.get_ToRoom(phase) else None
        # If the door has no 'ToRoom', it means it connects to the outside or is not a room boundary

        # Check if has origin room and, if it has destination room, if they are different
    
        if origin_room and origin_room.Id != destination_room.Id if destination_room else True:
            return True
        return False
    except Exception as e:
        print(e)
        pass

def calc_area_ambientes_com_soleira(door_list, room_num):
    soleiras_ambiente = {room_num: []}

    for door in door_list:
        try:
            if not door_connects_different_rooms(door, phase):
                continue

            origin_room = door.get_FromRoom(phase)
            if not origin_room or get_room_number(origin_room) != room_num:
                continue

            room_num = get_room_number(origin_room)
            print(room_num, " - ", get_name(origin_room))

            door_type = doc.GetElement(door.GetTypeId())
            if not door_type:
                print("⚠️ Tipo da porta não encontrado:", get_name(door))
                continue

            param_width = door_type.get_Parameter(DB.BuiltInParameter.DOOR_WIDTH)
            if not param_width:
                print("⚠️ Parâmetro de largura não encontrado na porta:", get_name(door))
                continue

            door_width = param_width.AsDouble()

            # checagem segura do host
            if not door.Host:
                print("⚠️ Porta sem host:", get_name(door))
                continue

            host_wall_type = doc.GetElement(door.Host.GetTypeId())
            if not host_wall_type:
                print("⚠️ Tipo da parede hospedeira não encontrado:", get_name(door))
                continue

            estrutura = host_wall_type.GetCompoundStructure()
            if not estrutura:
                print("⚠️ Parede sem estrutura composta:", get_name(door))
                continue

            host_wall_width = estrutura.GetWidth()
            area_soleira = door_width * host_wall_width

            soleiras_ambiente[room_num].append(area_soleira)

            # parâmetros compartilhados
            param_area_ambiente_com_soleiras = origin_room.LookupParameter("ÁREA AMBIENTE C/ SOLEIRAS")
            param_area_soleiras = origin_room.LookupParameter("ÁREA TOTAL DE SOLEIRAS")
            param_contagem_soleiras = origin_room.LookupParameter("CONTAGEM SOLEIRAS")

            missing_params = []
            if not param_area_ambiente_com_soleiras:
                missing_params.append("ÁREA AMBIENTE C/ SOLEIRAS")
            if not param_area_soleiras:
                missing_params.append("ÁREA TOTAL DE SOLEIRAS")
            if not param_contagem_soleiras:
                missing_params.append("CONTAGEM SOLEIRAS")

            if missing_params:
                forms.alert(
                    "Faltam parâmetros compartilhados no ambiente '{}':\n\n{}".format(
                        room_num,
                        "\n".join(missing_params)
                    ),
                    title="Parâmetros ausentes",
                    warn_icon=True
                )
                return

            contagem_soleiras_ambiente = len(soleiras_ambiente[room_num])
            soma_areas = sum(soleiras_ambiente[room_num])
            new_room_area = get_room_area(origin_room) + soma_areas

            t = DB.Transaction(doc, "Registrar áreas de soleiras no ambiente")
            t.Start()
            param_area_soleiras.Set(soma_areas)
            param_area_ambiente_com_soleiras.Set(new_room_area)
            param_contagem_soleiras.Set(contagem_soleiras_ambiente)
            t.Commit()

        except Exception as e:
            forms.alert(
                "Erro ao calcular área de soleiras no ambiente '{}':\n\n{}".format(
                    room_num,
                    str(e)
                ),
                title="Erro na execução",
                warn_icon=True
            )
            return


# Listar todos os ambientes disponíveis com número e nome
rooms = interface.rooms
room_choices = ["{} - {}".format(get_room_number(r), get_name(r)) for r in rooms]

# Abrir modal de seleção múltipla
selected = forms.SelectFromList.show(
    room_choices,
    multiselect=True,
    title="Selecionar ambiente(s)",
    button_name="Calcular área útil real (com soleiras)"
)

if not selected:
    forms.alert("Nenhum ambiente selecionado.", title="Aviso", warn_icon=True)
else:
    for sel in selected:
        # extrai só o núme<ro antes do " - " para passar pra função
        room_num = sel.split(" - ")[0]
        calc_area_ambientes_com_soleira(regular_doors, room_num)

# for room in interface.rooms:
#     calc_area_ambientes_com_soleira(regular_doors, get_room_number(room))


# # coletar o parametro fromRoom de cada porta

# # relacionar cada ambiente do projeto com as portas que se originam dele
# # descobrir a area da soleira de cada porta e armazenar em um dicionário
# # somar a area das soleiras e associar ao ambiente via dois parametros compartilhados: area soleiras e area corrigida do ambiente (area original + area soleiras)
# # criar um arquivo CSV com os dados coletados: a area final de cada ambiente deve ser a area ROOM_AREA + a soma das areas de soleira de cada porta da qual
