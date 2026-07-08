from __future__ import annotations

import logging
from datetime import datetime

from models.bons_de_pesee import BonDePesee, normaliser_espece


logger = logging.getLogger(__name__)


class AdapterBizerba:
    def adapter(self, ligne_brute: dict[str, str]) -> BonDePesee:
        numero_lot = self._champ_obligatoire(ligne_brute, "Num_Lot")
        date_pesee = self._date_depuis_fr(self._champ_obligatoire(ligne_brute, "Date_Pesee"), ligne_brute)
        poids_carcasse = self._decimal_fr(self._champ_obligatoire(ligne_brute, "Pds_Carcasse"), ligne_brute)
        poids_decoupe = self._decimal_fr(self._champ_obligatoire(ligne_brute, "Pds_Decoupe"), ligne_brute)
        categorie_classement = self._champ_obligatoire(ligne_brute, "Classe")
        source_balance = self._champ_obligatoire(ligne_brute, "Balance")
        espece = self._espece_optionnelle(ligne_brute, "Espece")

        self._verifier_poids(poids_carcasse, poids_decoupe, ligne_brute)

        return BonDePesee(
            numero_lot=numero_lot,
            date_pesee=date_pesee,
            poids_carcasse_kg=poids_carcasse,
            poids_decoupe_kg=poids_decoupe,
            categorie_classement=categorie_classement,
            source_balance=source_balance,
            espece=espece,
        )

    def _espece_optionnelle(self, ligne_brute: dict[str, str], cle: str) -> str:
        try:
            return normaliser_espece(ligne_brute.get(cle))
        except ValueError as exc:
            self._ligne_ignored(ligne_brute, str(exc))
            raise

    def _champ_obligatoire(self, ligne_brute: dict[str, str], cle: str) -> str:
        valeur = ligne_brute.get(cle, "")
        if valeur is None or not str(valeur).strip():
            self._ligne_ignored(ligne_brute, f"Champ obligatoire manquant: {cle}")
            raise ValueError(f"Champ obligatoire manquant: {cle}")
        return str(valeur).strip()

    def _date_depuis_fr(self, valeur: str, ligne_brute: dict[str, str]):
        for format_date in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(valeur, format_date).date()
            except ValueError:
                continue

        self._ligne_ignored(ligne_brute, f"Date invalide pour Bizerba: {valeur}")
        raise ValueError(f"Date invalide pour Bizerba: {valeur}")

    def _decimal_fr(self, valeur: str, ligne_brute: dict[str, str]) -> float:
        try:
            return float(valeur.replace(" ", "").replace(",", "."))
        except ValueError as exc:
            self._ligne_ignored(ligne_brute, f"Nombre invalide pour Bizerba: {valeur}")
            raise ValueError(f"Nombre invalide pour Bizerba: {valeur}") from exc

    def _verifier_poids(self, poids_carcasse: float, poids_decoupe: float, ligne_brute: dict[str, str]) -> None:
        if poids_carcasse <= 0:
            self._ligne_ignored(ligne_brute, "Le poids de carcasse doit être strictement positif")
            raise ValueError("Le poids de carcasse doit être strictement positif")
        if poids_decoupe <= 0:
            self._ligne_ignored(ligne_brute, "Le poids de découpe doit être strictement positif")
            raise ValueError("Le poids de découpe doit être strictement positif")

    def _ligne_ignored(self, ligne_brute: dict[str, str], raison: str) -> None:
        logger.warning("Ligne ignorée par AdapterBizerba: %s | %s", raison, ligne_brute)
