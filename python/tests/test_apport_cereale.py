from __future__ import annotations

import sys
from datetime import date
from pathlib import Path


PYTHON_DIR = Path(__file__).resolve().parents[1]
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from models.apport_cereale import ApportCereale


def _apport(taux_humidite_pct: float) -> ApportCereale:
    return ApportCereale(
        numero_apport="APP-001",
        date_apport=date(2026, 7, 2),
        site_collecte="Silo Nord",
        cereale="ble_tendre",
        poids_net_kg=1200.0,
        taux_humidite_pct=taux_humidite_pct,
        source_systeme="ERP",
    )


def test_rendement_normal_pas_d_alerte() -> None:
    apport = _apport(14.0)

    assert apport.est_en_alerte() is False


def test_rendement_trop_bas_pas_d_alerte_pour_humidite() -> None:
    apport = _apport(10.0)

    assert apport.est_en_alerte() is False


def test_rendement_trop_haut_declenche_alerte() -> None:
    apport = _apport(15.1)

    assert apport.est_en_alerte() is True


def test_rendement_egal_au_seuil_min_pas_d_alerte() -> None:
    apport = _apport(15.0)

    assert apport.est_en_alerte() is False

