from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import responses


PYTHON_DIR = Path(__file__).resolve().parents[1]
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from pipeline import run_pipeline
from adapters.lecteur_csv import lire_csv


def _bizerba_sample_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "samples" / "bizerba_export.csv"


@responses.activate
def test_pipeline_bout_en_bout_logiviande_avec_api_mocker() -> None:
    endpoint = "http://localhost:8080/lots"

    def callback(request):
        payload = json.loads(request.body.decode("utf-8"))
        response_body = {
            "id": payload["numero_lot"],
            "rendement_pct": round((payload["poids_decoupe_kg"] / payload["poids_carcasse_kg"]) * 100, 2),
            "alerte": True,
        }
        return (201, {"Content-Type": "application/json"}, json.dumps(response_body))

    responses.add_callback(
        responses.POST,
        endpoint,
        callback=callback,
        content_type="application/json",
    )

    fichier = _bizerba_sample_path()
    lignes_lues = lire_csv(fichier)
    resultats = run_pipeline(fichier, "logiviande", False)

    assert len(resultats) == len(lignes_lues)

    reussites = [resultat for resultat in resultats if resultat["succes"]]
    echecs = [resultat for resultat in resultats if not resultat["succes"]]

    assert len(reussites) > 0
    assert len(echecs) > 0
    assert any(resultat["objet_normalise"].est_en_alerte("bovin") for resultat in reussites)
    assert any(resultat["objet_normalise"].espece == "porc" for resultat in reussites)
    assert len(responses.calls) == len(reussites)
