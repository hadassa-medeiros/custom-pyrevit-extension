# -*- coding: utf-8 -*-
import clr

clr.AddReference('RevitAPI')
import Autodesk.Revit.DB as DB
import Autodesk.Revit.UI as UI


__title__     = "detect cad lines"
__author__    = "Hadassa Medeiros"
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

# doc = uidoc.Document
app = __revit__.Application
double_to_meter_divisor = 3.28084

cad_imports = DB.FilteredElementCollector(doc).OfClass(DB.ImportInstance).ToElements()
model_lines = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Lines).ToElements()
for m in model_lines:
    if m.LineStyle.Name == "Parede" and m.GeometryCurve.IsBound == True:
        level = m.SketchPlane
        start_point = m.GeometryCurve.GetEndPoint(0)
        end_point = m.GeometryCurve.GetEndPoint(1)
        line = DB.Line.CreateBound(start_point, end_point)
        wall_type = DB.FilteredElementCollector(doc).OfClass(DB.WallType).FirstElement()

        # Create new wall element
        wall_types_collector = DB.FilteredElementCollector(doc).OfClass(DB.WallType).FirstElement()

        try:
            t = DB.Transaction(doc, "Create new wall instance from cad lines")
            t.Start()
            new_wall = DB.Wall.Create(doc, line, wall_type.Id, level.Id, 10, 0, False, False)

        except:
            pass
            
        t.Commit()
        




# # print(cad_imports)
# for cad_import in cad_imports:
#     id_cad = cad_import.Id
#     typeid_cad = cad_import.GetTypeId()
#     # print(DB.Element.GetEntity(tipo_cad))
#     cad_instance = doc.GetElement(id_cad)
#     cad_type = doc.GetElement(typeid_cad)
#     cad_filename = cad_type.Category.Name
#     subcategories = cad_type.Category.SubCategories
#     print(subcategories)
#     for cad_layer in subcategories:
#         channels = cad_layer.LineColor
#         cad_layer_rgb = [int(channels.Red), int(channels.Green), int(channels.Blue)]
#         if cad_layer.Name == ("Parede" or "Paredes") and cad_layer_rgb == [0,0,255]:
#             print(cad_layer.Id)
#                 # wall_types_collection = wall_types_collector.ToElements()
#                 # print(wall_types_collection)
                
#                 # for wall_type_instance in wall_types_collection:
#                 #     print(type(wall_type_instance.Name))
#                 #     # parameters = wall_type_instance.ParametersMap  # Obtém todos os parâmetros
#                 #     # for param in parameters:
#                 #     #     if param.Definition == "Tipo":
#                 #     #         print(param.Definition.Name)
#                 #     # print(wall_type_instance.ParametersMap().Element



#     # a = list(cad_type.GetDependentElements(DB.ElementClassFilter(DB.)))
    
# # DB.ImportInstance.DeleteEntity(cad_imports, any)