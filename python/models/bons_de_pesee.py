from dataclasses import dataclass
from datetime import date


SEUILS_RENDEMENT = {
    "bovin": {
        "alerte_basse": 35.0,
        "standard": 45.0,
        "alerte_haute": 60.0,
    },
    "porc": {
        "alerte_basse": 60.0,
        "standard": 72.0,
        "alerte_haute": 85.0,
    },
}


ALIAS_ESPECES = {
    "bovin": "bovin",
    "bovins": "bovin",
    "boeuf": "bovin",
    "cattle": "bovin",
    "beef": "bovin",
    "cow": "bovin",
    "porc": "porc",
    "porcs": "porc",
    "cochon": "porc",
    "pig": "porc",
    "pork": "porc",
    "swine": "porc",
}


def normaliser_espece(valeur: str | None, espece_par_defaut: str = "bovin") -> str:
    valeur_normalisee = str(valeur or "").strip().lower()
    if not valeur_normalisee:
        return espece_par_defaut

    espece = ALIAS_ESPECES.get(valeur_normalisee, valeur_normalisee)
    if espece not in SEUILS_RENDEMENT:
        raise ValueError(f"Espèce inconnue: {valeur_normalisee}")
    return espece


@dataclass
class BonDePesee:
    numero_lot: str
    date_pesee: date
    poids_carcasse_kg: float
    poids_decoupe_kg: float
    categorie_classement: str
    source_balance: str
    espece: str = "bovin"

    def calculer_rendement(self) -> float:
        """
        Calcule le rendement en pourcentage.
        """
        if self.poids_carcasse_kg <= 0:
            raise ValueError("Le poids de carcasse doit être supérieur à 0.")
        return (self.poids_decoupe_kg / self.poids_carcasse_kg) * 100

    def est_en_alerte(self, espece: str | None = None) -> bool:
        """
        Retourne True si le rendement est en dehors de la plage acceptable.
        Sans argument, utilise l'espèce portée par le lot.
        """
        espece_effective = normaliser_espece(espece or self.espece)
        seuils = SEUILS_RENDEMENT[espece_effective]

        rendement = self.calculer_rendement()
        return rendement < seuils["alerte_basse"] or rendement > seuils["alerte_haute"]

    def ecart_vs_standard(self, espece: str | None = None) -> float:
        """
        Retourne l'écart entre le rendement et le standard de l'espèce.
        Sans argument, utilise l'espèce portée par le lot.
        """
        espece_effective = normaliser_espece(espece or self.espece)
        seuils = SEUILS_RENDEMENT[espece_effective]

        rendement = self.calculer_rendement()
        return rendement - seuils["standard"]

    def to_dict(self) -> dict:
        """
        Retourne un dictionnaire représentant le bon de pesée.
        """
        return {
            "numero_lot": self.numero_lot,
            "date_pesee": self.date_pesee.isoformat(),
            "poids_carcasse_kg": self.poids_carcasse_kg,
            "poids_decoupe_kg": self.poids_decoupe_kg,
            "categorie_classement": self.categorie_classement,
            "source_balance": self.source_balance,
            "espece": self.espece,
        }
