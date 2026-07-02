from dataclasses import dataclass
from datetime import date


SEUILS_HUMIDITE = {
    "ble_tendre":  {"max": 15.0},
    "mais":        {"max": 14.0},
    "orge":        {"max": 14.5},
}

@dataclass
class ApportCereale:
    numero_apport: str
    date_apport: date
    site_collecte: str
    cereale: str
    poids_net_kg: float
    taux_humidite_pct: float
    source_systeme: str


    def est_en_alerte(self):
        """
        Retourne True si le taux d'humidité est supérieur au seuil maximal pour la céréale.
        """
        seuils = SEUILS_HUMIDITE.get(self.cereale)
        if seuils is None:
            raise ValueError(f"Céréale inconnue: {self.cereale}")

        return self.taux_humidite_pct > seuils["max"]

    def to_dict(self):
        """
        Retourne un dictionnaire représentant l'apport de céréale.
        """
        return {
            "numero_apport": self.numero_apport,
            "date_apport": self.date_apport.isoformat(),
            "site_collecte": self.site_collecte,
            "cereale": self.cereale,
            "poids_net_kg": self.poids_net_kg,
            "taux_humidite_pct": self.taux_humidite_pct,
            "source_systeme": self.source_systeme,
        }