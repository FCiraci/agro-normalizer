from __future__ import annotations

from typing import Protocol

from models.bons_de_pesee import BonDePesee

from adapters.adapter_bizerba import AdapterBizerba
from adapters.adapter_dini_argeo import AdapterDiniArgeo
from adapters.adapter_multivac import AdapterMultivac


class Adapter(Protocol):
    def adapter(self, ligne_brute: dict[str, str]) -> BonDePesee:
        ...


def get_adapter(source: str) -> Adapter:
    source_normalise = source.strip().lower().replace(" ", "_").replace("-", "_")

    if source_normalise.startswith("bizerba") or source_normalise.startswith("biz"):
        return AdapterBizerba()

    if source_normalise.startswith("dini") or source_normalise.startswith("argeo"):
        return AdapterDiniArgeo()

    if source_normalise.startswith("multivac") or source_normalise.startswith("multi"):
        return AdapterMultivac()

    raise ValueError(f"Source de balance inconnue: {source}")