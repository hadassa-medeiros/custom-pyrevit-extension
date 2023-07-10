# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as revit

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

ambientes_em_teste = []
ids = [1123256, 1123259, 618033, 1123262,1502389,1457521,2013802]

for id in ids:
    amb = doc.GetElement(revit.ElementId(id))
    ambientes_em_teste.append(amb)
# nome = amb_wcm.Name.Value #DUVIDA: não entendi pq o atributo Name nao pega aqui mas pegou p ver o nome da parede.
print('Localizadas coordenadas XYZ da bounding box dos seguintes elementos:')
for ambiente in ambientes_em_teste:
    ambiente_id = ambiente.Id.ToString()
    ambiente_name = ambiente.get_Parameter(revit.BuiltInParameter.ROOM_NAME).AsString()
    ambiente_level = ambiente.Level.Name
    ambiente_elem = doc.GetElement(revit.ElementId(int(ambiente_id)))
    ambiente_bbox = ambiente.get_BoundingBox(doc.ActiveView)
    ambiente_outline = revit.Outline(ambiente_bbox.Min,
                                     ambiente_bbox.Max)  # é a outline que se passa como arg pro método revit.BoundingBoxIntersectsFilter (e não um objeto tipo BoundingBoxXYZ
    cod_paredes = ambiente.LookupParameter('COD-REVEST_PAREDES')
    cod_piso = ambiente.LookupParameter('COD-REVEST_PISO')
    cod_teto = ambiente.LookupParameter('COD-REVEST_TETO')
    print('{} - {}'.format(ambiente_name, ambiente_level))

    ambiente_como_filtro = revit.BoundingBoxIntersectsFilter(ambiente_outline)  # Create filter
    collected_intersecting_elements = revit.FilteredElementCollector(doc).WherePasses(
        ambiente_como_filtro).ToElements()  # Use filter to retrieve elements
    # lista_python_collected_elements = ['Ambiente {}: {}'.format(ambiente),list(collected_intersecting_elements)]
    # Iterate over the elements
    categorias_em_PTBR = ['Paredes', 'Pisos', 'Forros']
    categorias_relevantes = [
        str(revit.BuiltInCategory.OST_Floors),
        str(revit.BuiltInCategory.OST_Walls),
        str(revit.BuiltInCategory.OST_Ceilings)
    ]
    cont_elem = 0
    for element in collected_intersecting_elements:
        if element.get_Parameter(revit.BuiltInParameter.ELEM_CATEGORY_PARAM).AsValueString() == 'Forros':
            print('forro localizado')