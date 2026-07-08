from __future__ import annotations

import sys
from pathlib import Path


PYTHON_DIR = Path(__file__).resolve().parents[1]
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from adapters.adapter_dini_argeo import AdapterDiniArgeo
from adapters.adapter_llm import AdapterLLM
from adapters.adapter_multivac import AdapterMultivac
from adapters.lecteur_csv import lire_csv


SAMPLES_DIR = Path(__file__).resolve().parents[2] / "data" / "samples"


def _normaliser_valides(fichier: str, adapter) -> list:
    objets = []
    for ligne in lire_csv(SAMPLES_DIR / fichier):
        try:
            objets.append(adapter.adapter(ligne))
        except ValueError:
            continue
    return objets


def test_exports_dini_et_multivac_ne_mettent_pas_tous_les_bovins_en_alerte() -> None:
    for fichier, adapter in (
        ("dini_argeo_export.csv", AdapterDiniArgeo()),
        ("multivac_export.csv", AdapterMultivac()),
    ):
        objets = _normaliser_valides(fichier, adapter)
        bovins = [objet for objet in objets if objet.espece == "bovin"]
        bovins_en_alerte = [objet for objet in bovins if objet.est_en_alerte()]

        assert len(bovins) > 100
        assert 0 < len(bovins_en_alerte) < len(bovins)


def test_exports_llm_de_mapping_passent_en_mode_mock() -> None:
    adapter = AdapterLLM(mock=True)

    for fichier in (
        "llm_export_fr_semicolon.csv",
        "llm_export_en_comma.csv",
        "llm_export_normalise_tab.csv",
    ):
        objets = _normaliser_valides(fichier, adapter)

        assert len(objets) == 6
        assert {objet.espece for objet in objets} == {"bovin", "porc"}
        assert all(not objet.est_en_alerte() for objet in objets)
