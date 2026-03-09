# -*- coding: utf-8 -*-
import clr
import csv
import codecs
import Autodesk.Revit.DB as DB
from pyrevit import forms


def _m_to_ft(metros):
    """Converte metros para pes (unidade interna do Revit)."""
    return round(metros * 3.28084, 5)


def _category_for_code(codigo):
    """Retorna a BuiltInCategory baseada no prefixo do codigo da esquadria.

    Padrao BR:
        J* -> Janela (OST_Windows)
        P* -> Porta  (OST_Doors)
    """
    prefix = codigo.strip().upper()[0] if codigo else ""
    if prefix == "J":
        return DB.BuiltInCategory.OST_Windows
    elif prefix == "P":
        return DB.BuiltInCategory.OST_Doors
    return None


def _set_dimension_param(symbol, param_names, value_ft):
    """Tenta setar um parametro de dimensao em um FamilySymbol.

    Percorre a lista de nomes possiveis (PT e EN) ate encontrar um valido.
    """
    for name in param_names:
        param = symbol.LookupParameter(name)
        if param and not param.IsReadOnly:
            param.Set(value_ft)
            return True
    return False


class CADToRevitMigrator:
    """Pipeline: Le esquadrias de CSV exportado de DWG e cria FamilyTypes no Revit."""

    # Nomes possiveis para os parametros de largura e altura
    WIDTH_PARAM_NAMES = ["Largura", "Width", "Rough Width"]
    HEIGHT_PARAM_NAMES = ["Altura", "Height", "Rough Height"]

    def __init__(self, csv_path, doc):
        self.csv_path = csv_path
        self.doc = doc
        self.esquadrias = self._load_csv(csv_path)
        self._base_symbols = {}  # cache: BuiltInCategory -> FamilySymbol

    # ------------------------------------------------------------------
    # Leitura de dados
    # ------------------------------------------------------------------

    def _load_csv(self, path):
        """Carrega lista de esquadrias do CSV.

        Colunas esperadas: Codigo, Largura, Altura (metros).
        """
        esquadrias = []
        with codecs.open(path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                codigo = row.get("Codigo", "").strip()
                if not codigo:
                    continue
                try:
                    largura = float(row.get("Largura", 0))
                    altura = float(row.get("Altura", 0))
                except (ValueError, TypeError):
                    print("AVISO: linha ignorada, valores invalidos: {}".format(row))
                    continue

                cat = _category_for_code(codigo)
                if cat is None:
                    print("AVISO: codigo '{}' nao reconhecido (esperado J* ou P*), ignorando.".format(codigo))
                    continue

                esquadrias.append({
                    "codigo": codigo,
                    "largura": largura,
                    "altura": altura,
                    "category": cat,
                })
        return esquadrias

    # ------------------------------------------------------------------
    # Resolucao de familia base
    # ------------------------------------------------------------------

    def _find_existing_symbol(self, category):
        """Busca um FamilySymbol existente na categoria informada."""
        collector = DB.FilteredElementCollector(self.doc).OfCategory(
            category
        ).WhereElementIsElementType().ToElements()

        for elem in collector:
            if isinstance(elem, DB.FamilySymbol):
                return elem
        return None

    def _load_family_from_file(self, category):
        """Pede ao usuario para selecionar um .rfa e carrega no documento."""
        cat_name = "janela" if category == DB.BuiltInCategory.OST_Windows else "porta"
        rfa_path = forms.pick_file(
            file_ext="rfa",
            title="Selecione uma familia de {} (.rfa)".format(cat_name)
        )
        if not rfa_path:
            return None

        # IronPython: LoadFamily com out parameter via clr.Reference
        family_ref = clr.Reference[DB.Family]()
        loaded = self.doc.LoadFamily(rfa_path, family_ref)
        if not loaded:
            print("ERRO: nao foi possivel carregar '{}'.".format(rfa_path))
            return None

        # Buscar novamente apos carregar
        return self._find_existing_symbol(category)

    def _get_base_symbol(self, category):
        """Retorna um FamilySymbol base para duplicar.

        Tenta cache -> existente -> carregar .rfa.
        """
        if category in self._base_symbols:
            return self._base_symbols[category]

        symbol = self._find_existing_symbol(category)
        if symbol is None:
            symbol = self._load_family_from_file(category)

        if symbol is not None:
            self._base_symbols[category] = symbol
        return symbol

    # ------------------------------------------------------------------
    # Verificacao de duplicatas
    # ------------------------------------------------------------------

    def _type_already_exists(self, codigo, category):
        """Verifica se ja existe um FamilySymbol com esse nome na categoria."""
        collector = DB.FilteredElementCollector(self.doc).OfCategory(
            category
        ).WhereElementIsElementType().ToElements()

        for elem in collector:
            if hasattr(elem, "Name") and elem.Name == codigo:
                return True
        return False

    # ------------------------------------------------------------------
    # Criacao de tipos
    # ------------------------------------------------------------------

    def _create_single_type(self, esquadria):
        """Cria um FamilySymbol para uma esquadria.

        Retorna o FamilySymbol criado ou None se falhar/ja existir.
        """
        codigo = esquadria["codigo"]
        category = esquadria["category"]

        if self._type_already_exists(codigo, category):
            print("  {} ja existe, pulando.".format(codigo))
            return None

        base = self._get_base_symbol(category)
        if base is None:
            print("ERRO: nenhuma familia base encontrada para '{}'. Pulando.".format(codigo))
            return None

        # Ativar o symbol base se necessario
        if not base.IsActive:
            base.Activate()
            self.doc.Regenerate()

        new_symbol = base.Duplicate(codigo)

        # Setar largura
        largura_ft = _m_to_ft(esquadria["largura"])
        if not _set_dimension_param(new_symbol, self.WIDTH_PARAM_NAMES, largura_ft):
            print("  AVISO: nao encontrou parametro de largura para '{}'.".format(codigo))

        # Setar altura
        altura_ft = _m_to_ft(esquadria["altura"])
        if not _set_dimension_param(new_symbol, self.HEIGHT_PARAM_NAMES, altura_ft):
            print("  AVISO: nao encontrou parametro de altura para '{}'.".format(codigo))

        return new_symbol

    def create_all_types(self):
        """Cria FamilyTypes para todas as esquadrias do CSV.

        Retorna dict {codigo: FamilySymbol} dos tipos criados.
        """
        if not self.esquadrias:
            print("Nenhuma esquadria encontrada no CSV.")
            return {}

        created = {}
        skipped = 0

        t = DB.Transaction(self.doc, "Importar esquadrias do CSV")
        t.Start()
        try:
            for esq in self.esquadrias:
                result = self._create_single_type(esq)
                if result is not None:
                    created[esq["codigo"]] = result
                    print("  {} criado: {:.2f}m x {:.2f}m".format(
                        esq["codigo"], esq["largura"], esq["altura"]
                    ))
                else:
                    skipped += 1
            t.Commit()
        except Exception as e:
            t.RollBack()
            print("ERRO durante criacao de tipos: {}".format(e))
            return {}

        # Resumo
        janelas = sum(1 for e in created.values()
                      if e.Category.Id.IntegerValue == int(DB.BuiltInCategory.OST_Windows))
        portas = len(created) - janelas
        print("\n--- Resumo ---")
        print("Janelas criadas: {}".format(janelas))
        print("Portas criadas:  {}".format(portas))
        print("Ignoradas (ja existiam): {}".format(skipped))
        return created
