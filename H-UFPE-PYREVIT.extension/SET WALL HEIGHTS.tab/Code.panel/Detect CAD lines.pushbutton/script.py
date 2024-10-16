# -*- coding: utf-8 -*-
import clr

clr.AddReference('RevitAPI')
import Autodesk.Revit.DB as DB
import Autodesk.Revit.UI as UI

__title__     = "detect cad lines"
__author__    = "Hadassa Medeiros"
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

app = __revit__.Application
double_to_meter_divisor = 3.28084

# Coletar todas as linhas do modelo
model_lines = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Lines).ToElements()

# Coletar o primeiro tipo de parede disponível
wall_type = DB.FilteredElementCollector(doc).OfClass(DB.WallType).FirstElement()
if not wall_type:
    print("Nenhum tipo de parede encontrado.")

# Coletar o primeiro nível disponível
level = DB.FilteredElementCollector(doc).OfClass(DB.Level).FirstElement()
if not level:
    print("Nenhum nível encontrado.")

horizontal_lines = []
vertical_lines = []


def find_line_pair(line_list, first_line):
    for line in line_list:
        # print(round(0.49212598425128817, 6))
        # print(round(abs(first_line.GeometryCurve.GetEndPoint(0)[1] - line.GeometryCurve.GetEndPoint(0)[1]), 6))
        if round(abs(first_line.GeometryCurve.GetEndPoint(0)[1] - line.GeometryCurve.GetEndPoint(0)[1]), 6) == 0.492126:
            return (first_line, line)

# criar tuplas com funcao acima

for line in model_lines:
    if line.LineStyle.Name == "DPP-PAREDE" and line.GeometryCurve.IsBound:
        # print(line.GeometryCurve.GetEndPoint(0)[0])
        x_startpoint = line.GeometryCurve.GetEndPoint(0)[0]
        x_endpoint = line.GeometryCurve.GetEndPoint(1)[0]
        if x_startpoint - x_endpoint == 0:
            vertical_lines.append(line)
        else:
            y_startpoint = line.GeometryCurve.GetEndPoint(0)[1]
            y_endpoint = line.GeometryCurve.GetEndPoint(1)[1]
            horizontal_lines.append(line)

# print(len(horizontal_lines), vertical_lines)
for horizontal_line in horizontal_lines:
    tuple = find_line_pair(horizontal_lines, horizontal_line)
    print(tuple[0].GeometryCurve.GetEndPoint(0), 'tupla--------------------', tuple[1].GeometryCurve.GetEndPoint(0))
        # Verificar se level e wall_type estão definidos
    if wall_type and level and tuple is not None:
        start_point = tuple[0].GeometryCurve.GetEndPoint(0)
        # print(start_point)
        end_point = tuple[0].GeometryCurve.GetEndPoint(1)
        bound_line = DB.Line.CreateBound(start_point, end_point)

        t = DB.Transaction(doc, "Create new wall instance from cad lines")
        # t.Start()
        # try:
        #     new_wall = DB.Wall.Create(doc, bound_line, wall_type.Id, level.Id, 10, 0, False, False)
        #     print("Parede criada entre {} e {}.".format(start_point, end_point))
        # except Exception as e:
        #     print("Erro ao criar a parede: {}".format(e))
        #     pass
        # t.Commit()
print('Ok')

# for l in vertical_lines:
# ???




