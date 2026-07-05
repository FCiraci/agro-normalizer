from __future__ import annotations

import json
import logging
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

import requests

from adapters.adapter_factory import get_adapter
from adapters.adapter_llm import AdapterLLM
from adapters.lecteur_csv import lire_csv
from config.llm_keys import ANTHROPIC_API_KEY


logger = logging.getLogger(__name__)


# Bloc de configuration des points d'entrée API par module.
JAVA_ENDPOINTS = {
    "logiviande": "http://localhost:8080/lots",
    "silos": "http://localhost:8080/apports",
}


# Bloc principal du pipeline de normalisation et de transmission.
def run_pipeline(filepath: str | Path, module: str, use_llm: bool) -> list[dict[str, Any]]:
    chemin = Path(filepath)
    module_normalise = _normaliser_module(module)

    if not chemin.exists():
        message = f"Fichier introuvable: {chemin}"
        logger.error(message)
        return [_resultat_erreur(None, message)]

    if chemin.stat().st_size == 0:
        message = f"Fichier vide: {chemin}"
        logger.info(message)
        return []

    try:
        lignes = lire_csv(chemin)
    except UnicodeDecodeError as exc:
        message = f"Encoding inconnu pour le fichier {chemin}: {exc}"
        logger.error(message)
        return [_resultat_erreur(None, message)]

    if not lignes:
        message = f"Aucune ligne exploitable dans le fichier: {chemin}"
        logger.info(message)
        return []

    try:
        source = _detecter_source(chemin, lignes[0], module_normalise)
        adapter = _resoudre_adapter(source, module_normalise, use_llm)
    except ValueError as exc:
        message = f"Balance inconnue ou adapter indisponible: {exc}"
        logger.error(message)
        return [_resultat_erreur(None, message)]

    endpoint = _resoudre_endpoint(module_normalise)

    resultats: list[dict[str, Any]] = []

    for index, ligne_brute in enumerate(lignes, start=1):
        try:
            objet_normalise = adapter.adapter(ligne_brute)
        except Exception as exc:
            message = f"Ligne {index} ignorée lors de la normalisation: {exc}"
            logger.warning(message)
            resultats.append(_resultat_erreur(None, str(exc)))
            continue

        try:
            _verifier_rendement_logiviande(objet_normalise)
        except ValueError as exc:
            message = f"Ligne {index} rejetée: {exc}"
            logger.warning(message)
            resultats.append(_resultat_erreur(objet_normalise, str(exc)))
            continue

        try:
            reponse = _poster_objet(endpoint, objet_normalise)
        except Exception as exc:
            message = f"Ligne {index} non transmise à l'API Java: {exc}"
            logger.error(message)
            resultats.append(_resultat_erreur(objet_normalise, str(exc)))
            continue

        resultats.append(
            {
                "succes": True,
                "objet_normalise": objet_normalise,
                "erreur_eventuelle": None,
                "reponse_api": reponse,
            }
        )

    return resultats


# Bloc utilitaire pour structurer une erreur de pipeline.
def _resultat_erreur(objet_normalise: Any, erreur: str) -> dict[str, Any]:
    return {
        "succes": False,
        "objet_normalise": objet_normalise,
        "erreur_eventuelle": erreur,
    }


# Bloc de résolution du module normalisé.
def _normaliser_module(module: str) -> str:
    module_normalise = module.strip().lower()
    if "silo" in module_normalise:
        return "silos"
    return "logiviande"


# Bloc de détection de source à partir du fichier ou de la première ligne.
def _detecter_source(chemin: Path, premiere_ligne: dict[str, str], module: str) -> str:
    nom_fichier = chemin.stem.strip().lower().replace(" ", "_").replace("-", "_")

    candidats: list[str] = [nom_fichier]
    for cle in ("source_balance", "source_systeme", "Balance", "balance", "Source_Balance"):
        valeur = premiere_ligne.get(cle)
        if valeur:
            candidats.append(valeur)

    if module == "silos":
        for cle in ("site_collecte", "Site_Collecte", "site", "SITE"):
            valeur = premiere_ligne.get(cle)
            if valeur:
                candidats.append(valeur)

    for candidat in candidats:
        if candidat:
            texte = str(candidat).strip().lower().replace(" ", "_").replace("-", "_")
            if texte:
                return texte

    raise ValueError("Impossible de détecter la source du fichier")


# Bloc de sélection de l'adapter selon la source et le mode LLM.
def _resoudre_adapter(source: str, module: str, use_llm: bool):
    if use_llm:
        # Sans clé API, l'adapter LLM bascule en mode mock déterministe.
        return AdapterLLM(mock=not bool(ANTHROPIC_API_KEY), module=module)

    return get_adapter(source)


# Bloc de résolution du point de terminaison Java.
def _resoudre_endpoint(module: str) -> str:
    try:
        return JAVA_ENDPOINTS[module]
    except KeyError as exc:
        raise ValueError(f"Module inconnu: {module}") from exc


# Bloc de serialisation robuste pour l'objet normalisé.
def _serialiser_objet(objet: Any) -> dict[str, Any]:
    if hasattr(objet, "to_dict") and callable(objet.to_dict):
        return objet.to_dict()

    if is_dataclass(objet):
        return asdict(objet)

    if isinstance(objet, dict):
        return objet

    raise TypeError(f"Objet non sérialisable: {type(objet)!r}")


# Bloc d'envoi HTTP vers l'API Java.
def _poster_objet(endpoint: str, objet_normalise: Any) -> dict[str, Any]:
    try:
        response = requests.post(
            endpoint,
            json=_serialiser_objet(objet_normalise),
            timeout=10,
        )
    except requests.RequestException as exc:
        raise ValueError(f"API Java injoignable: {exc}") from exc

    if not response.ok:
        corps = response.text.strip()
        raise ValueError(f"API Java a répondu {response.status_code}: {corps or response.reason}")

    if not response.text.strip():
        return {"status_code": response.status_code}

    try:
        return response.json()
    except ValueError as exc:
        raise ValueError("Réponse API non-JSON") from exc


# Bloc de validation métier minimal avant POST vers Java.
def _verifier_rendement_logiviande(objet_normalise: Any) -> None:
    if hasattr(objet_normalise, "calculer_rendement"):
        rendement = objet_normalise.calculer_rendement()
        if rendement > 100:
            raise ValueError(f"Rendement supérieur à 100%: {rendement:.2f}")
