import sys
import types
import builtins
import unittest

# Provide stub for __revit__ used in the library
builtins.__revit__ = types.SimpleNamespace(
    ActiveUIDocument=types.SimpleNamespace(
        Document=types.SimpleNamespace(Application=None)
    )
)

# Provide stub modules for Autodesk.Revit.DB to satisfy imports in the library
Autodesk = types.ModuleType("Autodesk")
Autodesk.Revit = types.ModuleType("Autodesk.Revit")
Autodesk.Revit.DB = types.ModuleType("Autodesk.Revit.DB")
sys.modules.setdefault("Autodesk", Autodesk)
sys.modules.setdefault("Autodesk.Revit", Autodesk.Revit)
sys.modules.setdefault("Autodesk.Revit.DB", Autodesk.Revit.DB)

# Stub pyrevit package used in the library
pyrevit = types.ModuleType("pyrevit")
pyrevit.revit = types.SimpleNamespace()
pyrevit.forms = types.SimpleNamespace()
pyrevit.script = types.SimpleNamespace()
sys.modules.setdefault("pyrevit", pyrevit)

from lib.revit_doc_interface import metric_to_double, double_to_metric


class TestConversions(unittest.TestCase):
    def test_metric_to_double_and_back(self):
        values = [0, 1, 0.123, 2.345, 5.678, 0.5678]
        for val in values:
            as_double = metric_to_double(val)
            back_to_metric = double_to_metric(as_double)
            self.assertAlmostEqual(val, back_to_metric, delta=0.01)

    def test_double_to_metric_and_back(self):
        values = [0, 3.28084, 7.5, 15.245, 1.86286]
        for val in values:
            as_metric = double_to_metric(val)
            back_to_double = metric_to_double(as_metric)
            self.assertAlmostEqual(val, back_to_double, delta=0.02)


if __name__ == "__main__":
    unittest.main()

