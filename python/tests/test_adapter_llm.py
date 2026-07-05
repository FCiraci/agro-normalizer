from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest


PYTHON_DIR = Path(__file__).resolve().parents[1]
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from adapters.adapter_llm import AdapterLLM


def test_adapter_llm_mock_normalise_une_ligne_bizerba() -> None:
    adapter = AdapterLLM(mock=True)
    ligne = {
        "Num_Lot": "LOT-2026-101",
        "Date_Pesee": "05/04/2026",
        "Pds_Carcasse": "300,0",
        "Pds_Decoupe": "225,0",
        "Classe": "U3",
        "Balance": "BIZ-09",
    }

    bon = adapter.adapter(ligne)

    assert bon.numero_lot == "LOT-2026-101"
    assert bon.date_pesee == date(2026, 4, 5)
    assert bon.poids_carcasse_kg == 300.0
    assert bon.poids_decoupe_kg == 225.0
    assert bon.categorie_classement == "U3"
    assert bon.source_balance == "BIZ-09"


def test_adapter_llm_mock_normalise_une_ligne_multivac() -> None:
    adapter = AdapterLLM(mock=True)
    ligne = {
        "LOT": "LOT-2026-021",
        "DATE": "07/01/2026",
        "POIDS_C": "344.6",
        "POIDS_D": "262.8",
        "CLASSE": "E2",
        "BALANCE": "MULTI-01",
    }

    bon = adapter.adapter(ligne)

    assert bon.numero_lot == "LOT-2026-021"
    assert bon.date_pesee == date(2026, 1, 7)
    assert bon.poids_carcasse_kg == 344.6
    assert bon.source_balance == "MULTI-01"


def test_adapter_llm_mock_normalise_un_apport_silos() -> None:
    adapter = AdapterLLM(mock=True, module="silos")
    ligne = {
        "apport_id": "APP-B-201",
        "load_date": "2026-02-07",
        "collection_site": "Silo Est",
        "grain": "mais",
        "net_weight_kg": "980.0",
        "moisture_pct": "13.9",
        "system_name": "WMS",
    }

    apport = adapter.adapter(ligne)

    assert apport.numero_apport == "APP-B-201"
    assert apport.date_apport == date(2026, 2, 7)
    assert apport.cereale == "mais"
    assert apport.poids_net_kg == 980.0
    assert apport.taux_humidite_pct == 13.9


def test_adapter_llm_mock_echoue_explicitement_sur_entetes_inconnues() -> None:
    adapter = AdapterLLM(mock=True)

    with pytest.raises(ValueError, match="impossible de mapper"):
        adapter.adapter({"colonne_mystere": "valeur", "autre": "x"})


def test_adapter_llm_rejette_un_module_inconnu() -> None:
    with pytest.raises(ValueError, match="Module inconnu"):
        AdapterLLM(mock=True, module="inconnu")


def test_adapter_llm_rejette_un_json_invalide(monkeypatch: pytest.MonkeyPatch) -> None:
    adapter = AdapterLLM(mock=False, api_key="dummy")

    monkeypatch.setattr(adapter, "_appeler_anthropic", lambda _: "pas du json")

    with pytest.raises(ValueError, match="JSON invalide"):
        adapter._appeler_llm_et_parser_mapping("prompt")


def test_adapter_llm_rejette_un_mapping_incomplet() -> None:
    adapter = AdapterLLM(mock=True)
    ligne = {
        "Num_Lot": "LOT-2026-102",
        "Date_Pesee": "05/04/2026",
        "Pds_Carcasse": "300,0",
        "Pds_Decoupe": "225,0",
        "Classe": "U3",
    }

    with pytest.raises(ValueError, match="Aucune ligne brute exploitable|Champ obligatoire"):
        adapter._normaliser_ligne(
            ligne,
            {
                "numero_lot": "Num_Lot",
                "date_pesee": "Date_Pesee",
                "poids_carcasse_kg": "Pds_Carcasse",
                "poids_decoupe_kg": "Pds_Decoupe",
                "categorie_classement": "Classe",
                "source_balance": "Balance",
            },
        )
