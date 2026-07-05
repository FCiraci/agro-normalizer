from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from urllib import error as urllib_error
from urllib import request as urllib_request
from typing import Any

from config.llm_keys import ANTHROPIC_API_KEY
from models.bons_de_pesee import BonDePesee, SEUILS_RENDEMENT
from models.apport_cereale import ApportCereale


logger = logging.getLogger(__name__)

SCHEMAS_JSON_ATTENDUS = {
    "logiviande": {
        "numero_lot": "identifiant unique du lot",
        "date_pesee": "date au format YYYY-MM-DD",
        "poids_carcasse_kg": "poids carcasse en kg, float",
        "poids_decoupe_kg": "poids découpe en kg, float",
        "categorie_classement": "classement EUROP (E/U/R/O/P + chiffre)",
        "source_balance": "nom ou identifiant de la balance source",
    },
    "silos": {
        "numero_apport": "identifiant unique de l'apport",
        "date_apport": "date au format YYYY-MM-DD",
        "site_collecte": "nom du site de collecte",
        "cereale": "type de céréale (ble_tendre/mais/orge)",
        "poids_net_kg": "poids net en kg, float",
        "taux_humidite_pct": "taux d'humidité en pourcentage, float",
        "source_systeme": "nom ou identifiant du système source",
    },
}

PROMPTS_SYSTEME = {
    module: (
        "Tu es un assistant de normalisation de données pour la filière "
        + ("viande" if module == "logiviande" else "céréalière")
        + ".\n"
        "On te donne un extrait CSV brut (header + quelques lignes) et un schéma cible.\n"
        "Tu dois retourner UNIQUEMENT un objet JSON de mapping entre les colonnes\n"
        "sources et les champs cibles, sans explication.\n\n"
        f"Schéma cible :\n{json.dumps(schema, ensure_ascii=False, indent=2)}"
    )
    for module, schema in SCHEMAS_JSON_ATTENDUS.items()
}

# Synonymes de colonnes sources connus, utilisés par le mode mock pour simuler
# le mapping que produirait le LLM à partir des en-têtes.
SYNONYMES_COLONNES = {
    "logiviande": {
        "numero_lot": ("num_lot", "lot_number", "lot", "numero_lot"),
        "date_pesee": ("date_pesee", "weigh_date", "date"),
        "poids_carcasse_kg": ("pds_carcasse", "carcass_weight", "poids_c", "poids_carcasse_kg"),
        "poids_decoupe_kg": ("pds_decoupe", "cut_weight", "poids_d", "poids_decoupe_kg"),
        "categorie_classement": ("classe", "grade", "categorie_classement"),
        "source_balance": ("balance", "scale_id", "source_balance"),
        "espece": ("espece", "species"),
    },
    "silos": {
        "numero_apport": ("numero_apport", "apport_id", "apport"),
        "date_apport": ("date_apport", "load_date", "date"),
        "site_collecte": ("site_collecte", "collection_site", "site"),
        "cereale": ("cereale", "grain"),
        "poids_net_kg": ("poids_net", "net_weight_kg", "poids_net_kg"),
        "taux_humidite_pct": ("taux_humidite", "moisture_pct", "humidite", "taux_humidite_pct"),
        "source_systeme": ("source_systeme", "system_name", "systeme"),
    },
}

# Champs cibles facultatifs : leur absence dans le fichier source n'est pas une erreur.
CHAMPS_FACULTATIFS = {"espece"}

# Rétro-compatibilité : constantes historiques orientées Logiviande.
PROMPT_SYSTEME = PROMPTS_SYSTEME["logiviande"]
SCHEMA_JSON_ATTENDU = SCHEMAS_JSON_ATTENDUS["logiviande"]


class AdapterLLM:
    def __init__(
        self,
        mock: bool = False,
        api_key: str | None = None,
        model: str = "claude-sonnet-4-6",
        timeout_seconds: int = 30,
        module: str = "logiviande",
    ) -> None:
        if module not in SCHEMAS_JSON_ATTENDUS:
            raise ValueError(f"Module inconnu pour AdapterLLM: {module}")
        self.mock = mock
        self.api_key = api_key or ANTHROPIC_API_KEY
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.module = module

    def adapter(self, donnees_brutes: dict[str, Any]) -> BonDePesee | ApportCereale:
        if self.mock:
            return self._adapter_mock(donnees_brutes)

        prompt_utilisateur = self._construire_prompt(donnees_brutes)
        mapping = self._appeler_llm_et_parser_mapping(prompt_utilisateur)
        ligne_source = self._extraire_ligne_de_reference(donnees_brutes)

        return self._normaliser_ligne(ligne_source, mapping)

    def _adapter_mock(self, donnees_brutes: dict[str, Any]) -> BonDePesee | ApportCereale:
        ligne_source = self._extraire_ligne_de_reference(donnees_brutes)
        if not ligne_source:
            raise ValueError("Aucune ligne brute exploitable pour le mode mock")

        mapping = self._deduire_mapping_depuis_entetes(list(ligne_source.keys()))
        return self._normaliser_ligne(ligne_source, mapping)

    def _deduire_mapping_depuis_entetes(self, entetes: list[str]) -> dict[str, str]:
        """Simule le mapping que retournerait le LLM à partir des en-têtes connus."""
        entetes_normalises = {str(entete).strip().lower(): str(entete) for entete in entetes}
        mapping: dict[str, str] = {}
        introuvables: list[str] = []

        for champ_cible, synonymes in SYNONYMES_COLONNES[self.module].items():
            for synonyme in synonymes:
                if synonyme in entetes_normalises:
                    mapping[champ_cible] = entetes_normalises[synonyme]
                    break
            else:
                if champ_cible not in CHAMPS_FACULTATIFS:
                    introuvables.append(champ_cible)

        if introuvables:
            raise ValueError(
                "Mode mock: impossible de mapper les champs "
                f"{', '.join(introuvables)} depuis les en-têtes {entetes}"
            )

        return mapping

    def _construire_prompt(self, donnees_brutes: dict[str, Any]) -> str:
        entetes, lignes = self._extraire_entetes_et_lignes(donnees_brutes)
        lignes_extraites = lignes[:3]
        extrait_csv = [", ".join(entetes) if entetes else ""]
        extrait_csv.extend([", ".join(ligne) for ligne in lignes_extraites])

        return (
            f"{PROMPTS_SYSTEME[self.module]}\n\n"
            f"Schema JSON attendu:\n{json.dumps(SCHEMAS_JSON_ATTENDUS[self.module], ensure_ascii=False, indent=2)}\n\n"
            f"Extrait CSV brut:\n{chr(10).join(extrait_csv)}\n\n"
            "Retourne uniquement un objet JSON de mapping source -> cible."
        )

    def _appeler_llm_et_parser_mapping(self, prompt_utilisateur: str) -> dict[str, str]:
        if not self.api_key:
            raise ValueError("Clé Anthropic manquante. Renseigne ANTHROPIC_API_KEY dans .env ou utilise mock=True.")

        reponse_brute = self._appeler_anthropic(prompt_utilisateur)
        mapping = self._parser_json_mapping(reponse_brute)
        if not isinstance(mapping, dict):
            raise ValueError("Le JSON retourné par le LLM doit etre un objet JSON")

        mapping_nettoye: dict[str, str] = {}
        for cle, valeur in mapping.items():
            if not isinstance(cle, str) or not isinstance(valeur, str):
                raise ValueError("Le mapping JSON doit contenir uniquement des chaînes de caractères")
            mapping_nettoye[cle.strip()] = valeur.strip()

        champs_obligatoires = set(SCHEMAS_JSON_ATTENDUS[self.module])
        absents = [champ for champ in champs_obligatoires if champ not in mapping_nettoye]
        if absents:
            self._logger_ligne_ignored({"prompt": prompt_utilisateur}, f"Champs obligatoires absents du JSON du LLM: {', '.join(absents)}")
            raise ValueError(f"Champs obligatoires absents du JSON du LLM: {', '.join(absents)}")

        return mapping_nettoye

    def _appeler_anthropic(self, prompt_utilisateur: str) -> str:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "system": PROMPTS_SYSTEME[self.module],
            "messages": [
                {
                    "role": "user",
                    "content": prompt_utilisateur,
                }
            ],
        }

        requete = urllib_request.Request(
            url=url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib_request.urlopen(requete, timeout=self.timeout_seconds) as response:
                donnees = json.loads(response.read().decode("utf-8"))
        except urllib_error.HTTPError as exc:
            corps_erreur = exc.read().decode("utf-8", errors="replace") if exc.fp else str(exc)
            raise ValueError(f"Erreur Anthropic: {exc.code} - {corps_erreur}") from exc
        except urllib_error.URLError as exc:
            raise ValueError(f"Impossible de contacter Anthropic: {exc.reason}") from exc

        blocs = donnees.get("content", [])
        textes = [bloc.get("text", "") for bloc in blocs if isinstance(bloc, dict)]
        texte = "\n".join(textes).strip()
        if not texte:
            raise ValueError("Réponse vide de l'API Anthropic")
        return texte

    def _parser_json_mapping(self, texte: str) -> Any:
        texte_nettoye = texte.strip()
        try:
            return json.loads(texte_nettoye)
        except json.JSONDecodeError:
            extrait = self._extraire_json_depuis_texte(texte_nettoye)
            if extrait is None:
                self._logger_ligne_ignored({"reponse_llm": texte_nettoye}, "Le LLM a retourne un JSON invalide")
                raise ValueError("Le LLM a retourne un JSON invalide")

            try:
                return json.loads(extrait)
            except json.JSONDecodeError as exc:
                self._logger_ligne_ignored({"reponse_llm": texte_nettoye}, "Le LLM a retourne un JSON invalide")
                raise ValueError("Le LLM a retourne un JSON invalide") from exc

    def _extraire_json_depuis_texte(self, texte: str) -> str | None:
        match = re.search(r"\{.*\}", texte, flags=re.DOTALL)
        if match is None:
            return None
        return match.group(0)

    def _extraire_entetes_et_lignes(self, donnees_brutes: dict[str, Any]) -> tuple[list[str], list[list[str]]]:
        lignes = self._recuperer_lignes(donnees_brutes)
        if not lignes:
            return [], []

        entetes_brutes = donnees_brutes.get("header") or donnees_brutes.get("entetes") or []
        if isinstance(entetes_brutes, list) and entetes_brutes:
            entetes = [str(entete).strip() for entete in entetes_brutes]
        else:
            premiere_ligne = lignes[0]
            entetes = list(premiere_ligne.keys())

        lignes_formattees = [
            [str(ligne.get(entete, "")).strip() for entete in entetes]
            for ligne in lignes
            if isinstance(ligne, dict)
        ]
        return entetes, lignes_formattees

    def _recuperer_lignes(self, donnees_brutes: dict[str, Any]) -> list[dict[str, Any]]:
        for cle in ("rows", "lignes", "records", "data"):
            valeur = donnees_brutes.get(cle)
            if isinstance(valeur, list):
                return [ligne for ligne in valeur if isinstance(ligne, dict)]

        if all(isinstance(cle, str) for cle in donnees_brutes.keys()):
            if any(isinstance(valeur, str) for valeur in donnees_brutes.values()):
                return [donnees_brutes]

        return []

    def _extraire_premiere_ligne_brute(self, donnees_brutes: dict[str, Any]) -> dict[str, Any]:
        lignes = self._recuperer_lignes(donnees_brutes)
        return lignes[0] if lignes else {}

    def _extraire_ligne_de_reference(self, donnees_brutes: dict[str, Any]) -> dict[str, Any]:
        lignes = self._recuperer_lignes(donnees_brutes)
        return lignes[0] if lignes else {}

    def _normaliser_ligne(self, ligne_source: dict[str, Any], mapping: dict[str, str]) -> BonDePesee | ApportCereale:
        mapping_obligatoire = {c: s for c, s in mapping.items() if c not in CHAMPS_FACULTATIFS}
        valeurs = {champ_cible: self._valeur_mapee(ligne_source, champ_source, champ_cible) for champ_cible, champ_source in mapping_obligatoire.items()}

        if self.module == "silos":
            return self._construire_apport(ligne_source, valeurs)

        valeurs["espece"] = self._espece_optionnelle(ligne_source, mapping.get("espece"))
        return self._construire_bon_de_pesee(ligne_source, valeurs)

    def _espece_optionnelle(self, ligne_source: dict[str, Any], champ_source: str | None) -> str:
        valeur = ""
        if champ_source:
            valeur = str(ligne_source.get(champ_source) or "").strip().lower()
        if not valeur:
            return "bovin"
        if valeur not in SEUILS_RENDEMENT:
            self._logger_ligne_ignored(ligne_source, f"Espèce inconnue: {valeur}")
            raise ValueError(f"Espèce inconnue: {valeur}")
        return valeur

    def _construire_bon_de_pesee(self, ligne_source: dict[str, Any], valeurs: dict[str, str]) -> BonDePesee:
        numero_lot = valeurs["numero_lot"]
        date_pesee = self._parser_date(valeurs["date_pesee"])
        poids_carcasse_kg = self._parser_float(valeurs["poids_carcasse_kg"], "poids_carcasse_kg")
        poids_decoupe_kg = self._parser_float(valeurs["poids_decoupe_kg"], "poids_decoupe_kg")
        categorie_classement = valeurs["categorie_classement"]
        source_balance = valeurs["source_balance"]

        if poids_carcasse_kg <= 0:
            self._logger_ligne_ignored(ligne_source, "Le poids de carcasse doit être strictement positif")
            raise ValueError("Le poids de carcasse doit être strictement positif")
        if poids_decoupe_kg <= 0:
            self._logger_ligne_ignored(ligne_source, "Le poids de découpe doit être strictement positif")
            raise ValueError("Le poids de découpe doit être strictement positif")

        return BonDePesee(
            numero_lot=numero_lot,
            date_pesee=date_pesee,
            poids_carcasse_kg=poids_carcasse_kg,
            poids_decoupe_kg=poids_decoupe_kg,
            categorie_classement=categorie_classement,
            source_balance=source_balance,
            espece=valeurs.get("espece", "bovin"),
        )

    def _construire_apport(self, ligne_source: dict[str, Any], valeurs: dict[str, str]) -> ApportCereale:
        numero_apport = valeurs["numero_apport"]
        date_apport = self._parser_date(valeurs["date_apport"])
        site_collecte = valeurs["site_collecte"]
        cereale = valeurs["cereale"]
        poids_net_kg = self._parser_float(valeurs["poids_net_kg"], "poids_net_kg")
        taux_humidite_pct = self._parser_float(valeurs["taux_humidite_pct"], "taux_humidite_pct")
        source_systeme = valeurs["source_systeme"]

        if poids_net_kg <= 0:
            self._logger_ligne_ignored(ligne_source, "Le poids net doit être strictement positif")
            raise ValueError("Le poids net doit être strictement positif")

        return ApportCereale(
            numero_apport=numero_apport,
            date_apport=date_apport,
            site_collecte=site_collecte,
            cereale=cereale,
            poids_net_kg=poids_net_kg,
            taux_humidite_pct=taux_humidite_pct,
            source_systeme=source_systeme,
        )

    def _valeur_mapee(self, ligne_source: dict[str, Any], champ_source: str, champ_cible: str) -> str:
        valeur = ligne_source.get(champ_source)
        if valeur is None or str(valeur).strip() == "":
            self._logger_ligne_ignored(ligne_source, f"Champ obligatoire absent: {champ_cible} ({champ_source})")
            raise ValueError(f"Champ obligatoire absent: {champ_cible} ({champ_source})")
        return str(valeur).strip()

    def _parser_date(self, valeur: str):
        for format_date in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(valeur, format_date).date()
            except ValueError:
                continue
        raise ValueError(f"Date invalide: {valeur}")

    def _parser_float(self, valeur: str, nom_champ: str) -> float:
        try:
            return float(valeur.replace(",", "."))
        except ValueError as exc:
            self._logger_ligne_ignored({"valeur": valeur, "champ": nom_champ}, f"Valeur numerique invalide pour {nom_champ}: {valeur}")
            raise ValueError(f"Valeur numerique invalide pour {nom_champ}: {valeur}") from exc

    def _logger_ligne_ignored(self, ligne: dict[str, Any], raison: str) -> None:
        logger.warning("Ligne ignorée par AdapterLLM: %s | %s", raison, ligne)
