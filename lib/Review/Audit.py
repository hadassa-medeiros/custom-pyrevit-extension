import Autodesk.Revit.DB as DB
doc = __revit__.ActiveUIDocument.Document

def set_auditoria_bim(elem, texto):
    param = elem.LookupParameter("Auditoria CCBI")
    if param and param.StorageType == DB.StorageType.String:
        existente = param.AsString() or ""

        novo_valor = "{} ; {}".format(existente, texto) if existente else texto

        t = DB.Transaction(doc, "Atualizar Auditoria BIM")
        t.Start()
        try:
            param.Set(novo_valor)
        except Exception as e:
            print("Erro ao definir Auditoria CCBI em {}: {}".format(elem.Id, e))
        t.Commit()
# t = DB.Transaction(doc, "Auditoria BIM em lote")
# t.Start()
# for elem in elementos:
#     param = elem.LookupParameter("Auditoria CCBI")
#     if param and param.StorageType == DB.StorageType.String:
#         existente = param.AsString() or ""
#         novo_valor = existente + " | " + texto if existente else texto
#         param.Set(novo_valor)
# t.Commit()