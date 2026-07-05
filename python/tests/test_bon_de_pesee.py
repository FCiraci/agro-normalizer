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


def test_poids_carcasse_a_zero_ne_plante_pas_est_en_alerte() -> None:
    bon = _bon_de_pesee(poids_carcasse_kg=0.0, poids_decoupe_kg=10.0)

    with pytest.raises(ValueError, match="poids de carcasse"):
        bon.est_en_alerte("bovin")


def test_rendement_egal_au_seuil_max_ne_declenche_pas_alerte() -> None:
    bon = _bon_de_pesee(poids_carcasse_kg=100.0, poids_decoupe_kg=60.0)

    assert bon.est_en_alerte("bovin") is False


def test_rendement_superieur_a_100_est_detecte_en_alerte() -> None:
    bon = _bon_de_pesee(poids_carcasse_kg=100.0, poids_decoupe_kg=120.0)

    assert bon.calculer_rendement() == pytest.approx(120.0)
    assert bon.est_en_alerte("bovin") is True


def test_espece_inconnue_renvoie_une_exception_propre() -> None:
    bon = _bon_de_pesee(poids_carcasse_kg=100.0, poids_decoupe_kg=45.0)

    with pytest.raises(ValueError, match="Espèce inconnue"):
        bon.est_en_alerte("autruche")


def test_espece_par_defaut_est_bovin() -> None:
    bon = _bon_de_pesee(poids_carcasse_kg=100.0, poids_decoupe_kg=45.0)

    assert bon.espece == "bovin"
    assert bon.to_dict()["espece"] == "bovin"


def test_espece_portee_par_le_lot_est_utilisee_sans_argument() -> None:
    # 73 % : en alerte pour un bovin (35-60), normal pour un porc (60-85).
    bon_porc = BonDePesee(
        numero_lot="LOT-PORC",
        date_pesee=date(2026, 7, 2),
        poids_carcasse_kg=100.0,
        poids_decoupe_kg=73.0,
        categorie_classement="U3",
        source_balance="BAL-01",
        espece="porc",
    )

    assert bon_porc.est_en_alerte() is False
    assert bon_porc.est_en_alerte("bovin") is True


