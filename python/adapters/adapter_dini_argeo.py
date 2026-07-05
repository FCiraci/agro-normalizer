from __future__ import annotations

import logging
from datetime import datetime

from models.bons_de_pesee import BonDePesee


logger = logging.getLogger(__name__)


class AdapterDiniArgeo:
    def adapter(self, ligne_brute: dict[str, str]) -> BonDePesee:
        numero_lot = self._champ_obligatoire(ligne_brute, "lot_number")
        date_pesee = self._date_dini_argeo(self._champ_obligatoire(ligne_brute, "weigh_date"), ligne_brute)
        poids_carcasse = self._decimal_point(self._champ_obligatoire(ligne_brute, "carcass_weight"), ligne_brute)
        poids_decoupe = self._decimal_point(self._champ_obligatoire(ligne_brute, "cut_weight"), ligne_brute)
        categorie_classement = self._champ_obligatoire(ligne_brute, "grade")
        source_balance = self._champ_obligatoire(ligne_brute, "scale_id")

        self._verifier_poids(poids_carcasse, poids_decoupe, ligne_brute)

        return BonDePesee(
            numero_lot=numero_lot,
            date_pesee=date_pesee,
            poids_carcasse_kg=poids_carcasse,
            poids_decoupe_kg=poids_decoupe,
            categorie_classement=categorie_classement,
            source_balance=source_balance,
        )

    def _champ_obligatoire(self, ligne_brute: dict[str, str], cle: str) -> str:
        valeur = ligne_brute.get(cle, "")
        if valeur is None or not str(valeur).strip():
            self._ligne_ignored(ligne_brute, f"Champ obligatoire manquant: {cle}")
        return str(valeur).strip()

    def _date_dini_argeo(self, valeur: str, ligne_brute: dict[str, str]):
        for format_date in ("%d/%m/%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(valeur, format_date).date()
            except ValueError:
                continue

        self._ligne_ignored(ligne_brute, f"Date invalide pour Dini Argeo: {valeur}")
        raise ValueError(f"Date invalide pour Dini Argeo: {valeur}")

    def _decimal_point(self, valeur: str, ligne_brute: dict[str, str]) -> float:
        try:
            return float(valeur)
        except ValueError as exc:
            self._ligne_ignored(ligne_brute, f"Nombre invalide pour Dini Argeo: {valeur}")
            raise ValueError(f"Nombre invalide pour Dini Argeo: {valeur}") from exc

    def _verifier_poids(self, poids_carcasse: float, poids_decoupe: float, ligne_brute: dict[str, str]) -> None:
        if poids_carcasse <= 0:
            self._ligne_ignored(ligne_brute, "Le poids de carcasse doit être strictement positif")
            raise ValueError("Le poids de carcasse doit être strictement positif")
        if poids_decoupe <= 0:
            self._ligne_ignored(ligne_brute, "Le poids de découpe doit être strictement positif")
            raise ValueError("Le poids de découpe doit être strictement positif")

    def _ligne_ignored(self, ligne_brute: dict[str, str], raison: str) -> None:
        logger.warning("Ligne ignorée par AdapterDiniArgeo: %s | %s", raison, ligne_brute)
