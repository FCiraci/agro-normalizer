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


@dataclass
class BonDePesee:
    numero_lot: str
    date_pesee: date
    poids_carcasse_kg: float
    poids_decoupe_kg: float
    categorie_classement: str
    source_balance: str

    def calculer_rendement(self) -> float:
        """
        Calcule le rendement en pourcentage.
        """
        if self.poids_carcasse_kg <= 0:
            raise ValueError("Le poids de carcasse doit être supérieur à 0.")
        return (self.poids_decoupe_kg / self.poids_carcasse_kg) * 100

    def est_en_alerte(self, espece: str = "bovin") -> bool:
        """
        Retourne True si le rendement est en dehors de la plage acceptable.
        """
        seuils = SEUILS_RENDEMENT.get(espece)
        if seuils is None:
            raise ValueError(f"Espèce inconnue: {espece}")

        rendement = self.calculer_rendement()
        return rendement < seuils["alerte_basse"] or rendement > seuils["alerte_haute"]

    def ecart_vs_standard(self, espece: str) -> float:
        """
        Retourne l'écart entre le rendement et le standard de l'espèce.
        """
        seuils = SEUILS_RENDEMENT.get(espece)
        if seuils is None:
            raise ValueError(f"Espèce inconnue: {espece}")

        rendement = self.calculer_rendement()
        return rendement - seuils["standard"]
