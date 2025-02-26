# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
doc = __revit__.ActiveUIDocument.Document
from revit_doc_interface import (RevitDocInterface, pick_csv_file, remove_acentos, double_to_metric)
from pyrevit import (forms, script)
from Review.Phases import phase_created_is
from Review.Levels import check_levels
import os

doc = __revit__.ActiveUIDocument.Document


# script para revisao geral do modelo. seguir formato:
# try:
#   assert conferir_eixos()
# except AssertionError:
#   print("Eixos ausentes do projeto")


# 🔴 Todos os elementos modelados devem pertencer à fase Levantamento
interface = RevitDocInterface()
phase_created_is('LEVANTAMENTO')

# 🔴 A quantidade de niveis deve seguir a formula: qtdd pavimentos 
    # da edificcao/projeto x 2(pois para cada piso acabado ha um nivel _ossatura),
    # + 2 (Rua e Coberta)
    
# 🟡 O modelo deve conter apenas os níveis necessários para a edificação, sem excedentes não utilizados
# check_levels()

def comparar_modelo_com_planilha_areas():
  csv_file_path = pick_csv_file()
  # print(csv_file_path, type(csv_file_path))
  # script.show_file_in_explorer(csv_file_path)
  csv_table = script.load_csv(csv_file_path)
  # print(csv_table)

  # general building info from csv
  building_name = csv_table[4][0]
  rooms_totals_row = csv_table[-1]
  room_count = int(rooms_totals_row[0])
  room_area_count = rooms_totals_row[-2]
  levels_count_csv = 0

  # info by room from csv
  model_rooms_area_count = 0
  # dict_building_csv = {}
  for row in csv_table:
    if 'Nº AMBIENTE' in row[0] or 'DENOMINAÇÃO' in row[1]:
      levels_count_csv += 1
  #   # dict = {
  #   #   room_number: [room_name, room_area]
  #   #   # room_area: 
  #   # }
  #   if row[x] == :
  #     print(row[3])
      # dict_building_csv[row[0]] = {'NOME': row[1], 'AREA': row[2], 'USO': row[3]}
    # print(row)

  building_data_from_csv = {
    building_name: {
        'quantidade de ambientes': room_count, 
        'area util total': room_area_count,
        'quantidade de pavimentos': levels_count_csv,
      }
  }
  # print(building_data_from_csv)

  for room in interface.rooms:
    room_area = room.get_Parameter(
      DB.BuiltInParameter.ROOM_AREA
      ).AsValueString().split(' ')[0]
    model_rooms_area_count += float(room_area)

  building_data_from_model = {
    building_name: {
        'quantidade de ambientes': len(interface.rooms),
        # 'quantidade de pavimentos': [level for level in interface.levels if 'Pavimento' in level.Name],
        'area util total': model_rooms_area_count
      }
  }
  # print(building_data_from_model)
  
  # comparar dicionarios do csv e modelo e apontar diferencas se houver
  # for e in zip(building_data_from_csv, building_data_from_model):
  #   print(e)

comparar_modelo_com_planilha_areas()

# conferir se oos eixos estao corretos
def conferir_eixos():
  grid_objs = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
  grids_count = len(grid_objs)

  vertical_grids = []
  horizontal_grids = []
  tolerance = 2e-6
  if grids_count > 0:
    print('Ha ', grids_count, 'eixos no projeto: ', [grid.Name for grid in grid_objs]) 
    for grid in grid_objs:
      max_point_X = grid.GetExtents().MaximumPoint.X
      min_point_X = grid.GetExtents().MinimumPoint.X
      max_point_Y = grid.GetExtents().MaximumPoint.Y
      min_point_Y = grid.GetExtents().MinimumPoint.Y

      # print(max_point_Y - min_point_Y)

      if max_point_Y - min_point_Y < tolerance:
        horizontal_grids.append(grid.Name)
      elif max_point_X - min_point_X < tolerance:
        vertical_grids.append(grid.Name)
      # print(max_point, min_point)
    # print(vertical_grids, horizontal_grids)
    if horizontal_grids[0] == 'A' and vertical_grids[0] == '1' and len(horizontal_grids) > 1:
      return True

try:
  assert conferir_eixos()
except AssertionError:
  print("Eixos ausentes do projeto")

def walls_have_zero_base_offset():
  walls_with_base_offset = []
  for wall in interface.walls:
    
    wall_base_offset = wall.get_Parameter(DB.BuiltInParameter.WALL_BASE_OFFSET)

    if wall_base_offset.AsValueString() != '0.00':
      print(
          '{} - {} tem deslocamento da base igual a {} (deveria ser 0)'.format(
            wall.Name, 
            wall.get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_NAME).AsValueString(), 
            wall_base_offset.AsValueString()
            )
        )
      walls_with_base_offset.append(wall)
    # if attachment_bottom:
    #   print(attachment_bottom)


def walls_have_base_constrained_to_structural_level():
  incorrect_elements = []
  for wall in interface.walls:
      wall_base_constraint = wall.get_Parameter(DB.BuiltInParameter.WALL_BASE_CONSTRAINT)
      wall_base_constraint_str = wall_base_constraint.AsValueString()
      # print(wall_base_constraint.AsElementId())
      wall_base_constraint_level = doc.GetElement(wall_base_constraint.AsElementId())
      wall_base_constraint_level_str = wall_base_constraint_level.Name
      if 'ossatura' not in wall_base_constraint_str.lower() or wall_base_constraint_level.get_Parameter(
        DB.BuiltInParameter.LEVEL_IS_STRUCTURAL
      ).AsInteger() == 0:
        # print(wall)
        incorrect_elements.append(wall)
      
  # if len(incorrect_elements) > 0:
  #   call_to_model_correction = '{}'.format(len(incorrect_elements))
  #   print(call_to_model_correction)
  return len(incorrect_elements) == 0

walls_have_zero_base_offset()

try:
  assert walls_have_base_constrained_to_structural_level()
except AssertionError:
  print('Ha paredes cuja base esta associada a niveis de piso acabado (deve ser nivel _ossatura)')
"""
As categorias principais do modelo existem? (ex.: paredes, esquadrias)
dwgs devem estar presentes como vinculos CAD (e nao como imports)
 elementos estao corretamente categorizados
🟡 Os nomes dos ambientes devem seguir o padrão

limites de ambientes respeitam colunas ou pilares (nao os incluem)
as tags de ambiente devem ser dr uma familia especifica


🔴 Erros Críticos (Check Inicial – 15 min)
POR ENQUANTO, ISSO E MANUAL:
🔴 O modelo deve abrir sem erros e carregar corretamente
**🔴 Os arquivos vinculados devem carregar corretamente
**🔴 Os eixos de peças sanitárias devem estar corretamente posicionados e bloqueados 
(adicionar cota de bloqueio a partir da parede REV face mais proxima e paralela ao eixo da peca sanitaria)
🔴Os limites de ambientes devem estar corretos
    1. nao devem incluir areas de pilares/colunas, paredes
    2. devem abranger toda a area interna delimitada pelas paredes respectivas
    3. dentro de banheiros (WCs), as divisorias entre cabines individuais deve estar com o Parametro Delimitacao de ambientes desativado.

adicionar uma funcao para cada checagem abaixo
    🔴 PAREDES
    walls are used in layering systems, where each layer has a specific function and material
one core wall element represents the core/nucleus of the wall, plus the substract or pre-finishing layers
🟡 As bases de todas as paredes e pisos estruturais (EST) devem estar associadas ao nível de ossatura correspondente


🔴 walltype names must be
    composed by 3 parts: prefix["REV_", ALV_, "" + "wall name" + "wall.width in cm", all upper case except for the wall name(capitalized, no special characters)
    🟥 Structural and partition walls must be correctly differentiated

    REV_s:
    1. have their compound structre composed by only one layer
    2. this layer must 
        2.1 have its function (layer.Function) set to "Finish2"
        2.2 not have its material (layer.Material) empty (None or <By Category> or <Por Categoria>)
        2.3 have width 0.002 <= 0.01
            the closer the wall's width is to the minimum width allowed for non-Membrane-function layers, 
            the more accurate will be the finish area count by room, for the respective wall representing the finish material,
            given the current limitations of the script being developed to make these calculations

    if wall name prefix is anything other than standard
    correct it to the standard based on the unique characteristics of the walltype
    GENERICA_xCM
    ALV_s:
        1. have their core layer with function "Structure"
        2. have their core layer with structural materials, such as "Concrete" or "Masonry" (concreto ou alvenaria)
        3. have their compound structure's total thickness (equivalent to wall.Width) of x cm (need conversion from double to m to cm)
        4. have their surface (most external and most internal) layers 
            with function "Substrate" or "Finish1", but never "Finish2" or "Structure"
🔴 esquadrias devem estar conforme tabela csv exportada a partir do modelo dwg da edificacao. na ausencia de tabela no dwg,
    a referencia sera a representacao bidimensional em plantas baixas e elevacoes.

🟡 Estrutura Geral (BIM & Normas – 30 min)
🟡 Os níveis do projeto devem estar configurados corretamente (Térreo, Coberta e intermediários conforme necessário)
🟡 As cotas gerais e parciais devem estar presentes em todas as plantas baixas e cortes para garantir estabilidade das medidas ao longo do processo
🟡 Os ambientes devem estar nomeados (capitalizados) e numerados conforme dwg mais atual referencia
🟡🟡 As categorias de elementos devem estar corretas 
(porta é porta, parede é parede, mobiliario é mobiliario, etc.)
🟡 O modelo deve estar alinhado com a base DWG

🟡 devem existir os seguintes Parametros Compartilhados:
    associados a Ambientes: 'USO SPIUNET CLASSIFICACAO', 'USO CLASSIFICACAO', 'Revestimento Parede', Piso e Forro
🟡 devem existir os seguintes Parametros de projeto:
    'CAMPUS', 'CENTRO ACADEMICO'
    Paredes
    estruturais e de revestimento no sistema de paredes cebola
        1- bases devem estar associadas a nivel ossatura correspondente ao respectivo pavimento 
        2 - Topos devem estar conectados ao nivel ossatura do pavimento imediatamente superior
            (ex- 1o pavimento no dwg -> Terreo-Ossatura no modelo), nos casos de Terreo e pavimentos acima do terreo e abaixo da Coberta.
        3 - nas edificacoes em que nao haja ambientes no pavimento de Coberta, as platibandas devem ser modeladas como paredes com base associada a Coberta
            e topo nao associado, sendo a altura informada no campo Altura Desconectada, conforme projeto/levantamento.
        4 - em casos excepcionais, ou edificacoes cujo sistema de pavimentos seja diferente do caso padrao (Terreo, pavtos intermediarios
        e Coberta contendo apenas telhados, calhas, platibandas e ou lajes impermeabilizadas), consultar equipe.
    divisorias
        1- devem ter camadas conforme levantamento (ex: divisorias em granito -> camada de 2cm com material GRANITO e funcao da camada = Finish 1/Acabamento 1)
        2- em casos de divisorias mais complexas, como modulares com visores de vidro usadas em bibliotecas, por exemplo, devera ser usada Parede Cortina

🟡 pecas de mobiliario devem
    estar inseridas como Familias criadas a parte e importadas no modelo, e nunca como geometria modelada no local
    devem pertencer a categoria Mobiliario
    com exceção da Coberta, cada pavimento é representado por uma dupla de níveis: 
    o nível de projeto — que representa a altura do piso acabado — e o nível de ossatura. 
    A este último, devem estar associadas as Bases de todas as paredes (tanto estruturais como de revestimento) e os pisos tipo EST (lajes) do respectivo pavimento.
🟡 EIXOS
    Adicionar os Eixos de Projeto, numerados para o eixo X (1, 2, 3...) e alfabetizados para o eixo Y (A, B, C...). 
    Garantir que a interseção entre o eixo 1 e o eixo A coincida com o ponto (0,0,0) do projeto dwg. 
    Nos casos de edificações cujo levantamento ou documentação disponível nao explicite os eixos de projeto e as distâncias entre eles, 
    medir as distâncias entre todos os pilares, nos eixos X e Y, e 
    transferir as informações para a modelagem


✅ Refinamento - Organização do arquivo(Checklist do Trello – 30 min
🟢 Os materiais aplicados devem estar padronizados conforme biblioteca do template (AMPLIAR BIBLIOTECA a partir de revestimentos
observados em edificacoes com modelos ja concluidos)
✅ O modelo não deve conter erros bloqueantes
✅ A revisão final deve passar sem pendências
✅ O modelo deve estar limpo, sem elementos desnecessários (usar Limpar não utilizados apenas ao final da modelagem)
✅ As cotas auxiliares (AUX 3mm) devem estar configuradas corretamente e invisíveis em vistas para impressão
🟢 As tags e anotações devem estar legíveis e bem distribuídas





## Checklist de Verificação de Modelos BIM

### ⛔ Erros Críticos (Check Inicial – 15 min)
- O modelo deve abrir sem erros e carregar corretamente.
- As categorias principais do modelo devem existir (ex.: paredes, esquadrias, circulação).
- Os arquivos vinculados devem carregar corretamente.
- Não deve haver elementos obviamente quebrados ou faltando.
- A quantidade de níveis deve seguir a fórmula:
  - **Qtde de pavimentos da edificação/projeto × 2** (pois cada piso acabado tem um nível "ossatura")
  - **+2** (níveis extras: Rua e Coberta)
- O modelo deve conter apenas elementos essenciais (sem famílias, materiais, tipos, níveis ou vistas desnecessários).
- Todos os elementos modelados devem pertencer à fase **Levantamento**.
- Os eixos de peças sanitárias devem estar corretamente posicionados e bloqueados:
  - Adicionar cota de bloqueio a partir da parede **REV_** face mais próxima e paralela ao eixo da peça sanitária.
- Os limites de ambientes devem estar corretos:
  1. Não devem incluir áreas de pilares/colunas ou paredes.
  2. Devem abranger toda a área interna delimitada pelas paredes respectivas.
  3. Dentro de banheiros (WCs), as divisórias entre cabines individuais devem ter o parâmetro **Delimitação de Ambientes** desativado.

### 🟡 Estrutura Geral (BIM & Normas – 30 min)
- Os níveis do projeto devem estar configurados corretamente (Térreo, Coberta e intermediários conforme necessário).
- As bases de todas as paredes e pisos estruturais (EST) devem estar associadas ao nível de ossatura correspondente.
- O modelo deve conter apenas os níveis necessários para a edificação, sem excedentes não utilizados.
- As cotas gerais e parciais devem ser inseridas para garantir estabilidade das medidas ao longo do processo.
- Os ambientes devem estar **nomeados (capitalizados) e numerados** conforme a referência DWG mais atual.
- As categorias de elementos devem estar corretas (**portas são portas, paredes são paredes, mobiliário é mobiliário, etc.**).
- O modelo deve estar alinhado com a base DWG.
- As esquadrias devem estar conforme a **tabela CSV exportada** a partir do modelo DWG da edificação. Na ausência de tabela, a referência será a representação bidimensional em plantas baixas e elevações.
- Devem existir os seguintes **Parâmetros Compartilhados**:
  - Associados a Ambientes: **‘USO SPIUNET CLASSIFICACAO’, ‘USO CLASSIFICACAO’, ‘Revestimento Parede’, ‘Piso’ e ‘Forro’.**
- Devem existir os seguintes **Parâmetros de Projeto**:
  - **‘CAMPUS’, ‘CENTRO ACADÊMICO’.**
- As paredes estruturais e de revestimento (no sistema "paredes cebola") devem seguir:
  1. Bases associadas ao nível **ossatura** correspondente ao pavimento.
  2. Topos conectados ao nível **ossatura** do pavimento imediatamente superior (**ex.: 1º pavimento no DWG → Térreo-Ossatura no modelo**).

### ⚠ Validação de Paredes
- As paredes devem ser corretamente classificadas entre **Estruturais (ALV_)** e **Revestimentos (REV_)**.
- Nomes dos tipos de parede devem seguir o padrão:  
  - Prefixo: **REV_, ALV_, ou vazio.**
  - Nome: **descritivo da parede.**
  - Largura: **em cm.**
  - Exemplo: `REV_GESSO_1CM`.
- **REV_**:
  1. Devem ter apenas **uma camada** na estrutura composta.
  2. Essa camada deve:
     - Ter a função definida como **"Finish2"**.
     - Ter um material definido (**não pode ser "None", "<By Category>", ou "<Por Categoria>").**
     - Ter largura **entre 0.002m e 0.01m**.
- **ALV_**:
  1. Devem ter a camada **principal com função "Structure"**.
  2. Essa camada deve ter materiais estruturais (**ex.: Concreto ou Alvenaria**).
  3. A largura total da parede (wall.Width) deve ser convertida para **cm** e incluída no nome.
  4. As camadas **mais externa e interna** devem ter função **Substrate ou Finish1**, mas nunca **Finish2 ou Structure**.

---

Este checklist agora está mais estruturado e pronto para ser transformado em um código de verificação automática! 🚀




"""