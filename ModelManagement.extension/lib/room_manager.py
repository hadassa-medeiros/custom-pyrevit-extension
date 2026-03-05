# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB


class RoomManager:
    def __init__(self, doc):
        self.doc = doc

    def get_all_rooms(self):
        """Retorna todas as rooms do projeto."""
        return DB.FilteredElementCollector(self.doc)\
            .OfCategory(DB.BuiltInCategory.OST_Rooms)\
            .WhereElementIsNotElementType()\
            .ToElements()

    def get_room_info(self, room):
        """Retorna dict com info da room."""
        return {
            'name': room.Name,
            'area_sqm': room.Area / 10.764,
            'level': room.Level.Name,
            'can_hide': room.CanBeHidden,
        }

    def find_room_by_name(self, name):
        """Busca room por nome."""
        for room in self.get_all_rooms():
            if room.Name == name:
                return room
        return None
