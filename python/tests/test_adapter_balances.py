from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest


PYTHON_DIR = Path(__file__).resolve().parents[1]
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from adapters.adapter_bizerba import AdapterBizerba
from adapters.adapter_dini_argeo import AdapterDiniArgeo
from adapters.adapter_multivac import AdapterMultivac


def test_adapter_bizerba_normalise_une_ligne() -> None:
    bon = AdapterBizerba().adapter(
        {
            "Num_Lot": "LOT-2026-001",
            "Date_Pesee": "05/01/2026",
            "Pds_Carcasse": "312,4",
            "Pds_Decoupe": "228,7",
            "Classe": "U3",
            "Balance": "BIZ-01",
        }
    )

    assert bon.numero_lot == "LOT-2026-001"
    assert bon.date_pesee == date(2026, 1, 5)
    assert bon.poids_carcasse_kg == 312.4
    assert bon.poids_decoupe_kg == 228.7


def test_adapter_bizerba_lit_la_colonne_espece_optionnelle() -> None:
    ligne = {
        "Num_Lot": "LOT-2026-001",
        "Date_Pesee": "05/01/2026",
        "Pds_Carcasse": "312,4",
        "Pds_Decoupe": "228,7",
        "Classe": "U3",
        "Balance": "BIZ-01",
    }

    assert AdapterBizerba().adapter(ligne).espece == "bovin"
    assert AdapterBizerba().adapter({**ligne, "Espece": "Porc"}).espece == "porc"


def test_adapter_bizerba_rejette_une_espece_inconnue() -> None:
    with pytest.raises(ValueError, match="Espèce inconnue"):
        AdapterBizerba().adapter(
            {
                "Num_Lot": "LOT-2026-001",
                "Date_Pesee": "05/01/2026",
                "Pds_Carcasse": "312,4",
                "Pds_Decoupe": "228,7",
                "Classe": "U3",
                "Balance": "BIZ-01",
                "Espece": "autruche",
            }
        )


def test_adapter_bizerba_rejette_un_champ_obligatoire_manquant() -> None:
    with pytest.raises(ValueError, match="Champ obligatoire manquant: Classe"):
        AdapterBizerba().adapter(
            {
                "Num_Lot": "LOT-2026-001",
                "Date_Pesee": "05/01/2026",
                "Pds_Carcasse": "312,4",
                "Pds_Decoupe": "228,7",
                "Classe": "",
                "Balance": "BIZ-01",
            }
        )


def test_adapter_dini_argeo_rejette_un_champ_obligatoire_manquant() -> None:
    with pytest.raises(ValueError, match="Champ obligatoire manquant: scale_id"):
        AdapterDiniArgeo().adapter(
            {
                "lot_number": "LOT-2026-011",
                "weigh_date": "04/04/2026",
                "carcass_weight": "318.5",
                "cut_weight": "241.7",
                "grade": "U3",
            }
        )


def test_adapter_multivac_rejette_un_poids_negatif() -> None:
    with pytest.raises(ValueError, match="poids de découpe"):
        AdapterMultivac().adapter(
            {
                "LOT": "LOT-2026-029",
                "DATE": "10/03/2026",
                "POIDS_C": "331.2",
                "POIDS_D": "-176.4",
                "CLASSE": "P1",
                "BALANCE": "MULTI-05",
            }
        )
