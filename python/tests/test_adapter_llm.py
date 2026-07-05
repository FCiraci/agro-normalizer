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
