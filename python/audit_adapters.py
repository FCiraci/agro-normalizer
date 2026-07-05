"""Script d'audit section 3 : adapters statiques et LLM mock sur chaque sample.

Usage : python audit_adapters.py
Neutralise le POST HTTP pour tester uniquement la normalisation.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

PYTHON_DIR = Path(__file__).resolve().parent
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

import pipeline
from models.bons_de_pesee import BonDePesee
from models.apport_cereale import ApportCereale

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")

SAMPLES = Path(__file__).resolve().parents[1] / "data" / "samples"

FICHIERS = [
    ("bizerba_export.csv", "logiviande", BonDePesee),
    ("dini_argeo_export.csv", "logiviande", BonDePesee),
    ("multivac_export.csv", "logiviande", BonDePesee),
    ("site_a_export.csv", "silos", ApportCereale),
    ("site_b_export.csv", "silos", ApportCereale),
    ("site_c_export.csv", "silos", ApportCereale),
]

# Neutralise l'appel HTTP : on audite la normalisation, pas l'API.
pipeline._poster_objet = lambda endpoint, objet: {"status_code": 201}

for use_llm in (False, True):
    mode = "LLM mock" if use_llm else "statique"
    print(f"\n===== MODE {mode.upper()} =====")
    for nom_fichier, module, type_attendu in FICHIERS:
        chemin = SAMPLES / nom_fichier
        resultats = pipeline.run_pipeline(chemin, module, use_llm=use_llm)
        succes = [r for r in resultats if r["succes"]]
        echecs = [r for r in resultats if not r["succes"]]
        types_ok = all(isinstance(r["objet_normalise"], type_attendu) for r in succes)

        champs_attendus = {
            BonDePesee: {"numero_lot", "date_pesee", "poids_carcasse_kg", "poids_decoupe_kg", "categorie_classement", "source_balance"},
            ApportCereale: {"numero_apport", "date_apport", "site_collecte", "cereale", "poids_net_kg", "taux_humidite_pct", "source_systeme"},
        }[type_attendu]
        schema_ok = all(set(r["objet_normalise"].to_dict().keys()) == champs_attendus for r in succes)

        print(
            f"{nom_fichier:26s} [{module:10s}] -> {len(resultats)} lignes traitées, "
            f"{len(succes)} normalisées, {len(echecs)} rejetées | "
            f"type {type_attendu.__name__} OK: {types_ok} | schéma JSON OK: {schema_ok}"
        )
        for r in echecs:
            print(f"    REJET: {r['erreur_eventuelle']}")
