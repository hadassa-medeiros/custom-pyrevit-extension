from Autodesk.Revit.DB import Transaction, Element, FilteredElementCollector, BuiltInCategory
from Autodesk.Revit.UI import TaskDialog

doc = __revit__.ActiveUIDocument.Document

rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms)

for r in rooms:
	#antes, ao não fazer a conversão, o valor estava em pés, que descobri ser o default
	# do revit. logo, a conversão necessária para m²:
	area_amb = round(((r.Area*0.3048)/3.2808),2)
	nome = Element.Name.GetValue(r)
	print('{}-{}m'.format(nome, area_amb))
	nome_iniciais = nome[0:4]
	if nome_iniciais == 'SALA':
		print(nome + 'm²' + 'É SALA DE AULA')

print(rooms)
