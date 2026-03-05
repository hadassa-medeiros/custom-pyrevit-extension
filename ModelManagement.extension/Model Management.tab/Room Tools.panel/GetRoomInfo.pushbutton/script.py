# -*- coding: utf-8 -*-
from lib import RoomManager

doc = __revit__.ActiveUIDocument.Document

rm = RoomManager(doc)

for room in rm.get_all_rooms():
    info = rm.get_room_info(room)
    print("{} | {:.2f} m2 | {}".format(
        info['name'],
        info['area_sqm'],
        info['level']
    ))
