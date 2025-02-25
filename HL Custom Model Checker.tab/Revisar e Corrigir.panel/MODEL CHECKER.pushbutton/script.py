# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from revit_doc_interface import (RevitDocInterface, get_name)
from pyrevit import forms




"""
As categorias principais do modelo existem? (ex.: paredes, esquadrias)
dwgs devem estar presentes como vinculos CAD (e nao como imports)
 elementos estao corretamente categorizados
🟡 Os nomes dos ambientes devem seguir o padrão

limites de ambientes respeitam colunas ou pilares (nao os incluem)
as tags de ambiente devem ser dr uma familia especifica


🔴 Erros Críticos (Check Inicial – 15 min)
🔴 O modelo deve abrir sem erros e carregar corretamente
🔴 As categorias principais do modelo devem existir (paredes, esquadrias, circulação, etc.)
🔴 Os arquivos vinculados devem carregar corretamente
🔴 Não deve haver elementos obviamente quebrados ou faltando
a quantidade de niveis deve seguir a formula: qtdd pavimentos 
da edificcao/projeto x 2(pois para cada piso acabado ha um nivel _ossatura),
+ 2 (Rua e Coberta)
🔴 O modelo deve conter apenas elementos essenciais (sem famílias, materiais, tipos, níveis ou vistas desnecessários)

🔴 Todos os elementos modelados devem pertencer à fase Levantamento
🔴 Os eixos de peças sanitárias devem estar corretamente posicionados e bloqueados 
(adicionar cota de bloqueio a partir da parede REV face mais proxima e paralela ao eixo da peca sanitaria)
🔴Os limites de ambientes devem estar corretos
    1. nao devem incluir areas de pilares/colunas, paredes
    2. devem abranger toda a area interna delimitada pelas paredes respectivas
    3. dentro de banheiros (WCs), as divisorias entre cabines individuais deve estar com o Parametro Delimitacao de ambientes desativado.
🔴 PAREDES
    walls are used in layering systems, where each layer has a specific function and material
one core wall element represents the core/nucleus of the wall, plus the substract or pre-finishing layers


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


🟡 Estrutura Geral (BIM & Normas – 30 min)
🟡 Os níveis do projeto devem estar configurados corretamente (Térreo, Coberta e intermediários conforme necessário)
🟡 As bases de todas as paredes e pisos estruturais (EST) devem estar associadas ao nível de ossatura correspondente
🟡 O modelo deve conter apenas os níveis necessários para a edificação, sem excedentes não utilizados
🟡 As cotas gerais e parciais devem ser inseridas para garantir estabilidade das medidas ao longo do processo
🟡 Os ambientes devem estar nomeados (capitalizados) e numerados conforme dwg mais atual referencia
🟡🟡 As categorias de elementos devem estar corretas 
(porta é porta, parede é parede, mobiliario é mobiliario, etc.)
🟡 O modelo deve estar alinhado com a base DWG
🟡 esquadrias devem estar conforme tabela csv exportada a partir do modelo dwg da edificacao. na ausencia de tabela no dwg,
    a referencia sera a representacao bidimensional em plantas baixas e elevacoes.
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

🟢 Qualidade Arquitetônica (Geometria & Organização – 45 min)
🟢 As tags e anotações devem estar legíveis e bem distribuídas
🟢 O modelo deve estar limpo, sem elementos desnecessários (purge unused)
🟢 Os materiais aplicados devem estar padronizados conforme biblioteca do template (AMPLIAR BIBLIOTECA a partir de revestimentos
observados em edificacoes com modelos ja concluidos)

✅ Refinamento Final (Checklist do Trello – 30 min)
✅ O modelo não deve conter erros bloqueantes
✅ A revisão final deve passar sem pendências
✅ O modelo deve estar limpo (usar Limpar não utilizados apenas ao final da modelagem)
✅ As cotas auxiliares (AUX 3mm) devem estar configuradas corretamente e invisíveis em vistas para impressão
✅ Todos os elementos e pavimentos devem estar configurados de forma consistente para futuras atualizações





"""