class CalculateurSilos:

    @staticmethod
    def moyenne_ponderee_humidite(apports: list) -> float:
        if not apports:
            raise ValueError("La liste des apports ne peut pas être vide.")

        total_poids = sum(apport.poids_net_kg for apport in apports)
        if total_poids == 0:
            raise ValueError("La somme des poids ne peut pas être nulle.")

        total_humidite_ponderee = sum(
            apport.poids_net_kg * apport.taux_humidite_pct for apport in apports
        )
        return total_humidite_ponderee / total_poids

    @staticmethod
    def rapport_silo(apports: list) -> dict:
        moyenne_humidite = CalculateurSilos.moyenne_ponderee_humidite(apports)
        poids_total = sum(apport.poids_net_kg for apport in apports)
        nb_alertes = sum(1 for apport in apports if apport.est_en_alerte())

        return {
            "moyenne_humidite_ponderee": moyenne_humidite,
            "nb_apports": len(apports),
            "nb_alertes": nb_alertes,
            "poids_total_kg": poids_total,
        }