from __future__ import annotations

import logging
from datetime import datetime

from models.apport_cereale import ApportCereale


logger = logging.getLogger(__name__)


class AdapterSiteC:
    def adapter(self, ligne_brute: dict[str, str]) -> ApportCereale:
        numero_apport = self._champ_obligatoire(ligne_brute, "APPORT", "numero_apport")
        date_apport = self._date_fr(self._champ_obligatoire(ligne_brute, "DATE", "date_apport"), ligne_brute)
        site_collecte = self._champ_obligatoire(ligne_brute, "SITE", "site_collecte")
        cereale = self._champ_obligatoire(ligne_brute, "CEREALE", "cereale")
        poids_net_kg = self._decimal_point(self._champ_obligatoire(ligne_brute, "POIDS_NET", "poids_net_kg"), ligne_brute)
        taux_humidite_pct = self._decimal_point(self._champ_obligatoire(ligne_brute, "HUMIDITE", "taux_humidite_pct"), ligne_brute)
        source_systeme = self._champ_obligatoire(ligne_brute, "SYSTEME", "source_systeme")

        self._verifier_poids(poids_net_kg, ligne_brute)

        return ApportCereale(
            numero_apport=numero_apport,
            date_apport=date_apport,
            site_collecte=site_collecte,
            cereale=cereale,
            poids_net_kg=poids_net_kg,
            taux_humidite_pct=taux_humidite_pct,
            source_systeme=source_systeme,
        )

    def _champ_obligatoire(self, ligne_brute: dict[str, str], cle: str, nom_metier: str) -> str:
        valeur = ligne_brute.get(cle, "")
        if valeur is None or not str(valeur).strip():
            self._ligne_ignored(ligne_brute, f"Champ obligatoire manquant: {nom_metier} ({cle})")
            raise ValueError(f"Champ obligatoire manquant: {nom_metier}")
        return str(valeur).strip()

    def _date_fr(self, valeur: str, ligne_brute: dict[str, str]):
        try:
            return datetime.strptime(valeur, "%d/%m/%Y").date()
        except ValueError as exc:
            self._ligne_ignored(ligne_brute, f"Date invalide pour Site C: {valeur}")
            raise ValueError(f"Date invalide pour Site C: {valeur}") from exc

    def _decimal_point(self, valeur: str, ligne_brute: dict[str, str]) -> float:
        try:
            return float(valeur)
        except ValueError as exc:
            self._ligne_ignored(ligne_brute, f"Nombre invalide pour Site C: {valeur}")
            raise ValueError(f"Nombre invalide pour Site C: {valeur}") from exc

    def _verifier_poids(self, poids_net_kg: float, ligne_brute: dict[str, str]) -> None:
        if poids_net_kg <= 0:
            self._ligne_ignored(ligne_brute, "Le poids net doit être strictement positif")
            raise ValueError("Le poids net doit être strictement positif")

    def _ligne_ignored(self, ligne_brute: dict[str, str], raison: str) -> None:
        logger.warning("Ligne ignorée par AdapterSiteC: %s | %s", raison, ligne_brute)
