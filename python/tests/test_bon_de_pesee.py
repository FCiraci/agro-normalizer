from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest


PYTHON_DIR = Path(__file__).resolve().parents[1]
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from models.bons_de_pesee import BonDePesee


def _bon_de_pesee(poids_carcasse_kg: float, poids_decoupe_kg: float) -> BonDePesee:
    return BonDePesee(
        numero_lot="LOT-001",
        date_pesee=date(2026, 7, 2),
        poids_carcasse_kg=poids_carcasse_kg,
        poids_decoupe_kg=poids_decoupe_kg,
        categorie_classement="A",
        source_balance="BAL-01",
    )


def test_rendement_normal_pas_d_alerte() -> None:
    bon = _bon_de_pesee(poids_carcasse_kg=100.0, poids_decoupe_kg=45.0)

    assert bon.est_en_alerte("bovin") is False


def test_rendement_trop_bas_declenche_alerte() -> None:
    bon = _bon_de_pesee(poids_carcasse_kg=100.0, poids_decoupe_kg=34.9)

    assert bon.est_en_alerte("bovin") is True


def test_rendement_trop_haut_declenche_alerte() -> None:
    bon = _bon_de_pesee(poids_carcasse_kg=100.0, poids_decoupe_kg=60.1)

    assert bon.est_en_alerte("bovin") is True


def test_rendement_egal_au_seuil_min_ne_declenche_pas_alerte() -> None:
    bon = _bon_de_pesee(poids_carcasse_kg=100.0, poids_decoupe_kg=35.0)

    assert bon.est_en_alerte("bovin") is False


def test_poids_carcasse_a_zero_renvoie_une_exception_propre() -> None:
    bon = _bon_de_pesee(poids_carcasse_kg=0.0, poids_decoupe_kg=10.0)

    with pytest.raises(ValueError, match="poids de carcasse"):
        bon.calculer_rendement()


