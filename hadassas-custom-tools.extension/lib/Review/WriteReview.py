# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
doc = __revit__.ActiveUIDocument.Document

def write_review_comments(elem, texto):
    param = elem.LookupParameter("Comentários de Revisão por Elemento")
    if param and param.StorageType == DB.StorageType.String:
        existente = param.AsString() or ""

        novo_valor = "{}; {}".format(existente, texto) if existente else texto

        t = DB.Transaction(doc, "Inserir comentario de revisao em item do modelo")
        t.Start()
        
        try:
            param.Set(novo_valor)
        except Exception as e:
            print("Erro ao escrever comentario de revisao em {}: {}".format(elem.Id, e))
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