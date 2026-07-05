from __future__ import annotations

from typing import Any, Protocol

from models.bons_de_pesee import BonDePesee
from models.apport_cereale import ApportCereale

from adapters.adapter_bizerba import AdapterBizerba
from adapters.adapter_dini_argeo import AdapterDiniArgeo
from adapters.adapter_multivac import AdapterMultivac
from adapters.adapter_site_a import AdapterSiteA
from adapters.adapter_site_b import AdapterSiteB
from adapters.adapter_site_c import AdapterSiteC


class Adapter(Protocol):
    def adapter(self, ligne_brute: dict[str, str]) -> Any:
        ...


def get_adapter(source: str) -> Adapter:
    source_normalise = source.strip().lower().replace(" ", "_").replace("-", "_")

    if source_normalise.startswith("bizerba") or source_normalise.startswith("biz"):
        return AdapterBizerba()

    if source_normalise.startswith("dini") or source_normalise.startswith("argeo"):
        return AdapterDiniArgeo()

    if source_normalise.startswith("multivac") or source_normalise.startswith("multi"):
        return AdapterMultivac()

    if source_normalise.startswith("site_a") or source_normalise.startswith("sitea") or "nord" in source_normalise:
        return AdapterSiteA()

    if source_normalise.startswith("site_c") or source_normalise.startswith("sitec") or "ouest" in source_normalise:
        return AdapterSiteC()

    # "ouest" contient "est" : le test Site C doit passer avant et être exclu ici.
    if source_normalise.startswith("site_b") or source_normalise.startswith("siteb") or ("est" in source_normalise and "ouest" not in source_normalise):
        return AdapterSiteB()

    raise ValueError(f"Source de balance inconnue: {source}")