from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest


PYTHON_DIR = Path(__file__).resolve().parents[1]
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from models.apport_cereale import ApportCereale
from models.calculateur_silos import CalculateurSilos


def _apport(numero: str, poids_net_kg: float, taux_humidite_pct: float) -> ApportCereale:
    return ApportCereale(
        numero_apport=numero,
        date_apport=date(2026, 7, 2),
        site_collecte="Silo Nord",
        cereale="ble_tendre",
        poids_net_kg=poids_net_kg,
        taux_humidite_pct=taux_humidite_pct,
        source_systeme="ERP",
    )


def test_moyenne_ponderee_humidite_calcul_ok() -> None:
    apports = [
        _apport("APP-001", 1000.0, 14.0),
        _apport("APP-002", 500.0, 16.0),
    ]

    assert CalculateurSilos.moyenne_ponderee_humidite(apports) == pytest.approx(14.6666666667)


def test_moyenne_ponderee_humidite_rejette_liste_vide() -> None:
    with pytest.raises(ValueError, match="vide"):
        CalculateurSilos.moyenne_ponderee_humidite([])


def test_moyenne_ponderee_humidite_rejette_poids_nuls() -> None:
    apports = [_apport("APP-003", 0.0, 14.0)]

    with pytest.raises(ValueError, match="nulle"):
        CalculateurSilos.moyenne_ponderee_humidite(apports)


def test_rapport_silo_retourne_le_resume_attendu() -> None:
    apports = [
        _apport("APP-004", 1000.0, 14.0),
        _apport("APP-005", 500.0, 14.5),
    ]

    rapport = CalculateurSilos.rapport_silo(apports)

    assert rapport["moyenne_humidite_ponderee"] == pytest.approx(14.1666666667)
    assert rapport["nb_apports"] == 2
    assert rapport["nb_alertes"] == 0
    assert rapport["poids_total_kg"] == 1500.0