# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as db
from Autodesk.Revit.DB import FilteredElementCollector, CurveElementFilter, CurveElementType, ModelLine, WallType, Transaction
from pyrevit import forms

from utils import *

class Model:
    def __init__(self):
        self.uidoc = __revit__.ActiveUIDocument
        self.doc = self.uidoc.Document
        self.walltypes = FilteredElementCollector(self.doc).OfClass(WallType).ToElements()

    @property
    def lines(self):
        model_curves_filter = CurveElementFilter(CurveElementType.ModelCurve)
        model_curves = FilteredElementCollector(self.doc).WherePasses(model_curves_filter).WhereElementIsNotElementType().ToElements()
        model_lines = [curve for curve in model_curves if type(curve) is ModelLine]
        return model_lines
    
    #permitir chamar a propriedade layer de cada elemento de lines assim: model.line.layer
   
    def transaction(self, dbTransaction, message):
        t = Transaction(self.doc, message)
        try:
            t.Start()
            dbTransaction
            t.Commit()
        except:
            forms.alert('Erro ao tentar efetuar transação')

    def lines_by_style_name(self, line, ref_style_name):
        line_style = cleanup_str(line.LineStyle.Name)
        return [
            line for line in self.model_lines if 
                line_style == ref_style_name
            ]
    