# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as db
from Autodesk.Revit.DB import (
    FilteredElementCollector,
    CurveElementFilter,
    CurveElementType,
    ModelLine,
    WallType,
    Transaction,
)

class Convert:
    @staticmethod
    def m_to_ft(metros):
        return round(metros * 3.28084, 5)

    @staticmethod
    def ft_to_m(pes):
        return round(pes / 3.28084, 5)

class Model:
    def __init__(self, uidoc=None):
        self.uidoc = uidoc if uidoc is not None else __revit__.ActiveUIDocument
        self.doc = self.uidoc.Document
        self.walltypes = FilteredElementCollector(self.doc).OfClass(WallType).ToElements()

    @property
    def lines(self):
        model_curves_filter = CurveElementFilter(CurveElementType.ModelCurve)
        model_curves = FilteredElementCollector(self.doc).WherePasses(model_curves_filter).WhereElementIsNotElementType().ToElements()
        return [curve for curve in model_curves if type(curve) is ModelLine]


def is_vertical(line):
    if isinstance(line, db.ModelLine):
        startpoint_x = round(line.GeometryCurve.GetEndPoint(0).X, 3)
        endpoint_x = round(line.GeometryCurve.GetEndPoint(1).X, 3)
        return startpoint_x == endpoint_x
    return False


def is_horizontal(line):
    if isinstance(line, db.ModelLine):
        startpoint_y = round(line.GeometryCurve.GetEndPoint(0).Y, 3)
        endpoint_y = round(line.GeometryCurve.GetEndPoint(1).Y, 3)
        return startpoint_y == endpoint_y
    return False


def is_diagonal(line):
    return not (is_vertical(line) or is_horizontal(line))


def get_distance_between_lines(lineA, lineB, ref_direction="horizontal"):
    if ref_direction == "horizontal":
        distance = lineA.GeometryCurve.GetEndPoint(0).Y - lineB.GeometryCurve.GetEndPoint(0).Y
    elif ref_direction == "vertical":
        distance = lineA.GeometryCurve.GetEndPoint(0).X - lineB.GeometryCurve.GetEndPoint(0).X
    else:
        raise ValueError("ref_direction must be 'horizontal' or 'vertical'")
    return abs(distance)


def distance_between_lines_is_acceptable(distance_between_lines, minimum_cm=0.4):
    return Convert.ft_to_m(distance_between_lines) <= minimum_cm


def get_longest_line(lineA, lineB):
    return lineA if lineA.GeometryCurve.Length >= lineB.GeometryCurve.Length else lineB


def get_shortest_line(lineA, lineB):
    return lineA if lineA.GeometryCurve.Length < lineB.GeometryCurve.Length else lineB


def create_walltype_whith_one_layer_and_given_thickness(doc, walltypes, thickness_in_meters):
    basic_walltypes = [wt for wt in walltypes if str(wt.Kind) == "Basic"]
    if not basic_walltypes:
        raise RuntimeError('Nenhum WallType básico encontrado no modelo.')

    generic_walltype = basic_walltypes[0]
    transaction = Transaction(doc, "Create Wall Type with {}cm thickness".format(int(thickness_in_meters * 100)))
    transaction.Start()
    new_walltype = generic_walltype.Duplicate("Gen {}{}".format(round(int(thickness_in_meters * 100)), "cm"))
    compound_structure = generic_walltype.GetCompoundStructure()
    layer = compound_structure.GetLayers()[0]
    layer.Width = Convert.m_to_ft(thickness_in_meters)
    compound_structure.SetLayers([layer])
    db.WallType.SetCompoundStructure(new_walltype, compound_structure)
    transaction.Commit()
    return new_walltype


def get_existing_walls(doc):
    return FilteredElementCollector(doc).OfCategory(db.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()


def wall_exists_at_location(curve, doc, tolerance=0.1):
    new_start = curve.GetEndPoint(0)
    new_end = curve.GetEndPoint(1)
    new_mid = curve.Evaluate(0.5, True)

    for wall in get_existing_walls(doc):
        loc = wall.Location
        if not isinstance(loc, db.LocationCurve):
            continue
        ex_curve = loc.Curve
        ex_start = ex_curve.GetEndPoint(0)
        ex_end = ex_curve.GetEndPoint(1)
        ex_mid = ex_curve.Evaluate(0.5, True)

        if new_mid.DistanceTo(ex_mid) > tolerance:
            continue

        endpoints_match = (
            (new_start.DistanceTo(ex_start) < tolerance and new_end.DistanceTo(ex_end) < tolerance)
            or (new_start.DistanceTo(ex_end) < tolerance and new_end.DistanceTo(ex_start) < tolerance)
        )
        if endpoints_match:
            return True
    return False


def create_wall(startpoint, endpoint, wall_type, active_level, doc, height_m=2.0):
    curve = db.Line.CreateBound(startpoint, endpoint)
    if wall_exists_at_location(curve, doc):
        print("Parede ja existe nesta localizacao, pulando criacao. (curva: {} -> {})".format(startpoint, endpoint))
        return None

    altura = Convert.m_to_ft(height_m)
    wall = db.Wall.Create(
        doc,
        curve,
        wall_type.Id,
        active_level.Id,
        altura,
        0,
        False,
        False,
    )
    wall_location_line = wall.get_Parameter(db.BuiltInParameter.WALL_KEY_REF_PARAM)
    wall_location_line.Set(1)
    return wall
