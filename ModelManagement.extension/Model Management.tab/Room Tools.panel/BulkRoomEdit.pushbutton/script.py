# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from pyrevit import forms
from lib import RoomManager

doc = __revit__.ActiveUIDocument.Document

rm = RoomManager(doc)
rooms = rm.get_all_rooms()

if not rooms:
    forms.alert("Nenhuma room encontrada no projeto.")
else:
    room_names = [r.Name for r in rooms]
    selected = forms.SelectFromList.show(
        room_names,
        title="Selecione rooms para editar",
        multiselect=True
    )

    if selected:
        print("Rooms selecionadas: {}".format(len(selected)))
        for name in selected:
            room = rm.find_room_by_name(name)
            if room:
                info = rm.get_room_info(room)
                print("  {} | {:.2f} m2".format(info['name'], info['area_sqm']))
