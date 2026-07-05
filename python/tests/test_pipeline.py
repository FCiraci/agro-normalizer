from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest


PYTHON_DIR = Path(__file__).resolve().parents[1]
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

import pipeline
from models.bons_de_pesee import BonDePesee


def test_run_pipeline_retourne_vide_si_fichier_vide(tmp_path: Path) -> None:
    fichier = tmp_path / "vide.csv"
    fichier.write_text("", encoding="utf-8")

    assert pipeline.run_pipeline(fichier, "Logiviande", use_llm=False) == []


def test_run_pipeline_continue_si_api_injoignable(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fichier = tmp_path / "bizerba.csv"
    fichier.write_text(
        "Num_Lot;Date_Pesee;Pds_Carcasse;Pds_Decoupe;Classe;Balance\n"
        "LOT-001;05/01/2026;300,0;220,0;U3;BIZ-01\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(pipeline, "lire_csv", lambda _: [
        {
            "Num_Lot": "LOT-001",
            "Date_Pesee": "05/01/2026",
            "Pds_Carcasse": "300,0",
            "Pds_Decoupe": "220,0",
            "Classe": "U3",
            "Balance": "BIZ-01",
        }
    ])

    class FauxAdapter:
        def adapter(self, ligne_brute: dict[str, str]) -> BonDePesee:
            return BonDePesee(
                numero_lot=ligne_brute["Num_Lot"],
                date_pesee=date(2026, 1, 5),
                poids_carcasse_kg=300.0,
                poids_decoupe_kg=220.0,
                categorie_classement="U3",
                source_balance="BIZ-01",
            )

    monkeypatch.setattr(pipeline, "get_adapter", lambda _: FauxAdapter())
    monkeypatch.setattr(pipeline, "_poster_objet", lambda *_: (_ for _ in ()).throw(ValueError("API Java injoignable: refused")))

    resultats = pipeline.run_pipeline(fichier, "Logiviande", use_llm=False)

    assert len(resultats) == 1
    assert resultats[0]["succes"] is False
    assert resultats[0]["objet_normalise"] is not None
    assert "API Java injoignable" in resultats[0]["erreur_eventuelle"]


def test_run_pipeline_rejette_un_rendement_superieur_a_100(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fichier = tmp_path / "bizerba.csv"
    fichier.write_text(
        "Num_Lot;Date_Pesee;Pds_Carcasse;Pds_Decoupe;Classe;Balance\n"
        "LOT-900;05/01/2026;300,0;350,0;U3;BIZ-01\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(pipeline, "lire_csv", lambda _: [
        {
            "Num_Lot": "LOT-900",
            "Date_Pesee": "05/01/2026",
            "Pds_Carcasse": "300,0",
            "Pds_Decoupe": "350,0",
            "Classe": "U3",
            "Balance": "BIZ-01",
        }
    ])

    class FauxAdapter:
        def adapter(self, ligne_brute: dict[str, str]) -> BonDePesee:
            return BonDePesee(
                numero_lot=ligne_brute["Num_Lot"],
                date_pesee=date(2026, 1, 5),
                poids_carcasse_kg=300.0,
                poids_decoupe_kg=350.0,
                categorie_classement="U3",
                source_balance="BIZ-01",
            )

    appels_api: list[str] = []
    monkeypatch.setattr(pipeline, "get_adapter", lambda _: FauxAdapter())
    monkeypatch.setattr(pipeline, "_poster_objet", lambda *args: appels_api.append("appel") or {})

    resultats = pipeline.run_pipeline(fichier, "Logiviande", use_llm=False)

    assert len(resultats) == 1
    assert resultats[0]["succes"] is False
    assert "Rendement supérieur à 100%" in resultats[0]["erreur_eventuelle"]
    assert appels_api == []
