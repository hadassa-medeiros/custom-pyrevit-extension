# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

materiais_collector = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Materials)
ambientes_collector = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms)
paredes_collector =   DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls)
pisos_collector =     DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Floors)
forros_collector =    DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Ceilings)

materiais = materiais_collector.ToElements()
ambientes = ambientes_collector.ToElements()
pisos = pisos_collector.ToElements()
forros = forros_collector.ToElements()
paredes = paredes_collector.ToElements()
paredes_instancias = paredes_collector.WhereElementIsNotElementType().ToElements()
todos_elem_constr = [pisos_collector, forros_collector, paredes_collector]
ambientes_em_teste = []
# ids = [1123256, 1123259, 1123262, 1502389, 618033, 1123955, 1123958]
ids = [1123955] #copa mezanino

for id in ids:
    amb = doc.GetElement(DB.ElementId(id))
    ambientes_em_teste.append(amb)
print('Localizadas XYZ bounding box dos seguintes elementos:')

for amb in ambientes_em_teste:
    amb_level = amb.Level.Name
    amb_id = amb.Id.ToString()
    amb_name = amb.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
    amb_elem = doc.GetElement(DB.ElementId(int(amb_id)))
    amb_area_str = amb.LookupParameter('Área').AsValueString()
    amb_area = float((amb_area_str)[:5])
    fator_multipl_m2_para_double = (amb.LookupParameter('Área').AsDouble()) / amb_area_num
    amb_bbox = amb.get_BoundingBox(doc.ActiveView)
    amb_outline = DB.Outline(amb_bbox.Min,amb_bbox.Max)  # é a outline que se passa como arg pro método DB.BoundingBoxIntersectsFilter (e não um objeto tipo BoundingBoxXYZ

    cod_paredes = amb.LookupParameter('COD-REVEST_PAREDES')
    cod_paredes2 = amb.LookupParameter('COD-REVEST2_PAREDES')
    cod_piso = amb.LookupParameter('COD-REVEST_PISO')
    cod_teto = amb.LookupParameter('COD-REVEST_TETO')
    print('{} - {}-{}'.format(amb_name, amb_level, amb_area))

    amb_como_filtro = DB.BoundingBoxIntersectsFilter(amb_outline)# Create filter
    elementos_intersectantes = DB.FilteredElementCollector(doc).WherePasses(amb_como_filtro).ToElements()    # Use filter to retrieve elements
    # lista_python_collected_elements = ['Ambiente {}: {}'.format(amb),list(collected_intersecting_elements)]
    categorias_em_PTBR = ['Paredes', 'Pisos', 'Forros']

    forros_categ = str(DB.BuiltInCategory.OST_Ceilings)

    paredes_categ = str(DB.BuiltInCategory.OST_Walls)
    pisos_categ = str(DB.BuiltInCategory.OST_Floors)

    categorias_relevantes = [forros_categ, paredes_categ, pisos_categ]

    print('ENCONTRADOS os seguintes objetos:')
    for elem in intersecting_elements:
        # SEM O TRY/EXCEPT ELE NAO CONSEGUE ITERAR POR TODOS OS ELEMENTOS:
        try:
            # DEFINIÇÕES:
            categ = str(elem.Category.BuiltInCategory)

            if any(str(elem.Category.BuiltInCategory) == categoria for categoria in categorias_relevantes):
                print('{}, {}, cód. ID {}'.format(elem.Name, elem.Category.Name, elem.Id))
                elem_type_id = elem.GetTypeId()
                elem_type = doc.GetElement(elem_type_id)
                elem_estrut = DB.HostObjAttributes.GetCompoundStructure(elem_type)
                camadas = elem_estrut.GetLayers()
                quant_camadas = elem_estrut.LayerCount
                for camada in camadas:
                    mat_rev_parede = doc.GetElement(DB.ElementId(int(camada.MaterialId.ToString())))
                    print(mat_rev_parede.Name)
                    funcao = camada.Function.ToString()
                    if funcao == 'Finish2' or funcao == 'Membrane':
                        try:
                            if elem.Category.Name == 'Paredes':
                                # acessar objeto dentre lista Materiais a partir do id do mat. atribuído à camada de revestimento Finish2
                                mat_rev_parede = doc.GetElement(DB.ElementId(int(camada.MaterialId.ToString())))
                                for material in materiais:
                                    if material.Id == camada.MaterialId:
                                        revest_parede = material
                                        # print('ok, material associado a PAREDE:', revest_parede.Name)
                                t = DB.Transaction(doc, "aplicar cod revest a ambiente")
                                t.Start()
                                cod_paredes.Set(revest_parede.Id)
                                t.Commit()
                            elif elem.Category.Name == 'Pisos':
                                mat_rev_piso = doc.GetElement(DB.ElementId(int(camada.MaterialId.ToString())))
                                print(mat_rev_piso.Name, elem.Name)
                                for material in materiais:
                                    if material.Id == camada.MaterialId:
                                        revest_piso = material
                                        print('ok, material associado a PISO:', revest_piso.Name)
                                t = DB.Transaction(doc, "aplicar cod revest a ambiente")
                                t.Start()
                                cod_piso.Set(revest_piso.Id)
                                t.Commit()
                            elif categ == forros_categ:
                                forro_area = elem.LookupParameter('Área').AsValueString()
                                forro_area_num = float((forro_area)[:5])
                                if amb_area_num * .9 < forro_area_num < amb_area_num * 1.1:
                                    print('o forro do ambiente {} é: {}, {}, ID nº {}'.format(amb_name,elem.Name,elem.Category.Name,elem.Id))
                                    mat_rev_forro = doc.GetElement(DB.ElementId(int(camada.MaterialId.ToString())))
                                    print(mat_rev_forro.Name, elem.Name)
                                    for material in materiais:
                                        if material.Id == camada.MaterialId:
                                            revest_forro = material
                                            print('ok, material associado a FORRO:', revest_forro.Name)
                                    t = DB.Transaction(doc, "aplicar cod revest forro a ambiente")
                                    t.Start()
                                    cod_teto.Set(revest_forro.Id)
                                    t.Commit()
                        except AttributeError as e:
                            print('erro ao tentar printar nome do objeto:', camada.Id, e)
                    # elif camada.Function.ToString() == 'Membrane' or camada.LayerId == quant_camadas - 1:
                    # elif elem.Category.Name == 'Forros' and camada.LayerId == quant_camadas - 1:
                    #     print('elem.Category.Name')
                    #     mat_rev_forro = doc.GetElement(DB.ElementId(int(camada.MaterialId.ToString())))
                    #     print(mat_rev_forro.Name, elem.Name)
                    #     for material in materiais:
                    #         if material.Id == camada.MaterialId:
                    #             revest_forro = material
                    #             print('ok, material associado a FORRO:', revest_forro.Name)
                    #     t = DB.Transaction(doc, "aplicar cod revest forro a ambiente")
                    #     t.Start()
                    #     cod_teto.Set(revest_forro.Id)
                    #     t.Commit()
        except AttributeError:
            pass