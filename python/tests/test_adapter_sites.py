from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest


PYTHON_DIR = Path(__file__).resolve().parents[1]
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from adapters.adapter_factory import get_adapter
from adapters.adapter_bizerba import AdapterBizerba
from adapters.adapter_site_a import AdapterSiteA
from adapters.adapter_site_b import AdapterSiteB
from adapters.adapter_site_c import AdapterSiteC


def test_adapter_site_a_normalise_un_apport() -> None:
    adapter = AdapterSiteA()
    bon = adapter.adapter(
        {
            "Numero_Apport": "APP-A-001",
            "Date_Apport": "05/01/2026",
            "Site_Collecte": "Silo Nord",
            "Cereale": "ble_tendre",
            "Poids_Net": "1200,5",
            "Taux_Humidite": "14,2",
            "Source_Systeme": "ERP",
        }
    )

    assert bon.numero_apport == "APP-A-001"
    assert bon.date_apport == date(2026, 1, 5)
    assert bon.site_collecte == "Silo Nord"
    assert bon.poids_net_kg == 1200.5
    assert bon.taux_humidite_pct == 14.2


def test_adapter_site_b_normalise_un_apport() -> None:
    adapter = AdapterSiteB()
    bon = adapter.adapter(
        {
            "apport_id": "APP-B-001",
            "load_date": "2026-02-07",
            "collection_site": "Silo Est",
            "grain": "mais",
            "net_weight_kg": "980.0",
            "moisture_pct": "13.9",
            "system_name": "WMS",
        }
    )

    assert bon.numero_apport == "APP-B-001"
    assert bon.date_apport == date(2026, 2, 7)
    assert bon.cereale == "mais"
    assert bon.poids_net_kg == 980.0


def test_adapter_site_c_normalise_un_apport() -> None:
    adapter = AdapterSiteC()
    bon = adapter.adapter(
        {
            "DATE": "18/03/2026",
            "SYSTEME": "MES",
            "CEREALE": "orge",
            "HUMIDITE": "14.1",
            "APPORT": "APP-C-001",
            "POIDS_NET": "1100.0",
            "SITE": "Silo Ouest",
        }
    )

    assert bon.numero_apport == "APP-C-001"
    assert bon.date_apport == date(2026, 3, 18)
    assert bon.source_systeme == "MES"
    assert bon.taux_humidite_pct == 14.1


def test_adapter_site_a_rejette_un_poids_nul() -> None:
    adapter = AdapterSiteA()

    with pytest.raises(ValueError, match="poids net"):
        adapter.adapter(
            {
                "Numero_Apport": "APP-A-002",
                "Date_Apport": "05/01/2026",
                "Site_Collecte": "Silo Nord",
                "Cereale": "ble_tendre",
                "Poids_Net": "0",
                "Taux_Humidite": "14,2",
                "Source_Systeme": "ERP",
            }
        )


def test_adapter_factory_route_logiviande_et_silos() -> None:
    assert isinstance(get_adapter("Bizerba"), AdapterBizerba)
    assert isinstance(get_adapter("Site A Nord"), AdapterSiteA)
    assert isinstance(get_adapter("site_b"), AdapterSiteB)
    assert isinstance(get_adapter("site_c"), AdapterSiteC)
