"""Script d'audit section 5 : pipeline bout-en-bout Python -> API Java réelle.

Prérequis : l'API Spring Boot doit tourner sur http://localhost:8080.
Usage : python audit_e2e.py
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import requests

PYTHON_DIR = Path(__file__).resolve().parent
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from pipeline import run_pipeline, JAVA_ENDPOINTS

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")

SAMPLES = Path(__file__).resolve().parents[1] / "data" / "samples"

FICHIERS = [
    ("bizerba_export.csv", "logiviande"),
    ("dini_argeo_export.csv", "logiviande"),
    ("multivac_export.csv", "logiviande"),
    ("site_a_export.csv", "silos"),
    ("site_b_export.csv", "silos"),
    ("site_c_export.csv", "silos"),
]

erreurs_globales = 0

for use_llm in (False, True):
    mode = "LLM mock" if use_llm else "statique"
    print(f"\n===== E2E MODE {mode.upper()} =====")
    for nom_fichier, module in FICHIERS:
        resultats = run_pipeline(SAMPLES / nom_fichier, module, use_llm=use_llm)
        succes = [r for r in resultats if r["succes"]]
        echecs = [r for r in resultats if not r["succes"]]

        # Vérifie que chaque objet POSTé est bien relisible via GET /{id}.
        endpoint = JAVA_ENDPOINTS[module]
        introuvables = []
        for r in succes:
            identifiant = r["reponse_api"]["id"]
            reponse = requests.get(f"{endpoint}/{identifiant}", timeout=10)
            if reponse.status_code != 200:
                introuvables.append((identifiant, reponse.status_code))

        statut = "OK" if not introuvables else f"ECHEC GET: {introuvables}"
        if introuvables:
            erreurs_globales += 1
        print(
            f"{nom_fichier:26s} [{module:10s}] -> {len(succes)} POSTés/vérifiés en base, "
            f"{len(echecs)} rejetés localement | relecture GET: {statut}"
        )

# Vérification des alertes côté Java.
print("\n===== ALERTES COTE JAVA =====")
for module, endpoint in JAVA_ENDPOINTS.items():
    reponse = requests.get(f"{endpoint}/alertes", timeout=10)
    corps = reponse.json()
    print(f"GET {endpoint}/alertes -> [{reponse.status_code}] {len(corps)} alertes")
    for element in corps[:5]:
        print(f"    {element}")
    if len(corps) > 5:
        print(f"    ... et {len(corps) - 5} autres")

sys.exit(1 if erreurs_globales else 0)
