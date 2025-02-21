# -*- coding: utf-8 -*-
# o desafio e com base no nome do ambiente, ele ser inteloigente e ja classificar o uso

# atribuir classificacao de uso a ambientes com base no nome dado a eles

# 1- acessar room Name

import Autodesk.Revit.DB as DB
import json
import os
import codecs  # 🔥 Import necessário para compatibilidade com IronPython
from Autodesk.Revit.UI import TaskDialog
from revit_doc_interface import (RevitDocInterface, remove_acentos, get_project_parameter, normalize_param, get_name)

interface = RevitDocInterface()
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

# model_version = DB.BasicFileInfo.GetDocumentVersion(doc)
# model_path = DB.BasicFileInfo.CentralPath

uso_ccbi = [
    {"ADMINISTRACAO": []}, 
    "APOIO LABORATORIOS",
    "AUDITORIO",
    "BIBLIOTECA",
    "BIOTERIO",
    "CANTINA",
    "CIRCULACAO",
    "CONSULTORIO",
    "COPA",
    "GABINETE PROFESSOR",
    "INFORMATICA",
    "LABORATORIOS",
    "OUTROS",
    "POCO",
    "SALA DE AULA",
    "SERVICOS",
    "WC"
]

usos_spiunet = {
    "AREA DE ESCRITORIO": {
        "INDIVIDUAL": [
            "administracao", 
            "coordenacao", 
            "nucleo", 
            "secretaria", 
            "escolaridade", 
            "diretoria", 
            "centro", 
            "conselho departamental", 
            "departamento", 
            "escritorio", 
            "financas", 
            "gerencia",
            "recepcao"
                       ],
        "COLETIVO": [
            "reuniao", 
            "coworking"]
        },
    "AREA DE APOIO": [
        "auditorio",
        "copa",
        "sanitario",
        "wc",
        "vestiario",
        "guarita",
        "salas de motoristas",
        "espacos multiuso",
        "espacos de convivência",
        "refeitorios",
        "salas de arquivos correntes",
        "estacoes de autoatendimento",
        "reprografia", 
        "depositos voltado a vontade administrativa", 
        "manutencao predial"
    ],
    "AREA TECNICA": [
        "hall", 
        "acesso",
        "recepcao",
        "foyer",
        "corredor",
        "circulacao"
        "escada",
        "saida de emergencia",
        "incendio",
        "elevador",
        "reservatorio",
        "barrilete",
        "shaft",
        "switch",
        "medidor",
        "subestacao",
        "gerador",
        "quadro tecnico",
        "cofre",
        "garagem"
    ],
    "AREA ESPECIFICA": [
        "aula",
        "laboratorio",
        "restaurante",
        "cantina",
        "copa",
        "edificio garagem",
        "arquivos permanentes",
        "arquivo permanente"
    ]
}


# 🔎 Obtém todas as salas no modelo
for room in interface.rooms:
    room_name = get_name(room).lower()
    # print(room_name)
    for room_use_keywords in usos_spiunet.values():
        for keyword in room_use_keywords:
            # print(keyword)
            if keyword in room_name:
                print(keyword, '------',room_name)
                #abrir transacao
                t = DB.Transaction(doc, 'assign room use')
                room_use_spiunet = room.LookupParameter('USO SPIUNET CLASSIFICACAO')
                print(room_use_spiunet)
                t.Start ()
                room_use_spiunet.Set(keyword.capitalize())

                t.Commit()  


        

# 2- mapear o nome a uma das opcoes de classificacao de uso interno a ccbi
# 3 - mapear o nome OU o uso ccbi a uso spiunet (4)
# 4 - salvar os dois valores separadamente em dois parametros compartilhados associados a ambientes
# 5 - gravar dados no json com as infos do projeto e de seus ambientes
""