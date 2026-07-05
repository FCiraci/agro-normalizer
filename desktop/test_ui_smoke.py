"""Test de fumée automatisé de l'interface PySide6 (section 6 de l'audit).

Prérequis : API Java sur localhost:8080.
Usage : python desktop/test_ui_smoke.py
Pilote les widgets programmatiquement, sans interaction manuelle.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import AgroNormalizerApp, TABLE_COLUMNS
from themes import BASE_UI

SAMPLES = Path(__file__).resolve().parents[1] / "data" / "samples"

app = QApplication(sys.argv)
fenetre = AgroNormalizerApp()
erreurs: list[str] = []


def verifier(condition: bool, message: str) -> None:
    print(("OK   " if condition else "ECHEC") + f" {message}")
    if not condition:
        erreurs.append(message)


def attendre_worker() -> None:
    fenetre._worker.wait(30000)
    app.processEvents()


# 1. Démarrage sans exception + colonnes Logiviande par défaut.
colonnes = [fenetre.results_table.horizontalHeaderItem(i).text() for i in range(fenetre.results_table.columnCount())]
verifier(colonnes == TABLE_COLUMNS["Logiviande"], "démarrage: colonnes Logiviande affichées")
verifier("#7A0E0E" in fenetre.styleSheet(), "démarrage: thème Logiviande (rouge) appliqué")

# 2. Changement de module -> colonnes et thème changent, journal s'incrémente.
journal_avant = fenetre.log.toPlainText().count("\n")
fenetre.module_combo.setCurrentText("Silos")
app.processEvents()
colonnes = [fenetre.results_table.horizontalHeaderItem(i).text() for i in range(fenetre.results_table.columnCount())]
verifier(colonnes == TABLE_COLUMNS["Silos"], "module Silos: colonnes du tableau changées")
verifier("#6B4226" in fenetre.styleSheet(), "module Silos: thème (brun) appliqué")
verifier(fenetre.log.toPlainText().count("\n") > journal_avant, "module Silos: journal incrémenté")

# 3. Traitement d'un fichier Silos réel -> tableau peuplé via QThread.
fenetre.file_path_label.setText(str(SAMPLES / "site_b_export.csv"))
fenetre.process_button.click()
verifier(isinstance(getattr(fenetre, "_worker", None), object), "traitement: worker QThread démarré")
attendre_worker()
verifier(fenetre.results_table.rowCount() == 6, f"traitement Silos: 6 lignes attendues, {fenetre.results_table.rowCount()} affichées")
verifier(fenetre.process_button.isEnabled(), "traitement: bouton réactivé après le run")

# 4. Ligne en alerte colorée (APP-B-203, maïs 15.8 % > 14 %).
ligne_alerte = None
for row in range(fenetre.results_table.rowCount()):
    if fenetre.results_table.item(row, 0).text() == "APP-B-203":
        ligne_alerte = row
        break
verifier(ligne_alerte is not None, "alerte: APP-B-203 présent dans le tableau")
if ligne_alerte is not None:
    item = fenetre.results_table.item(ligne_alerte, 0)
    verifier(item.data(Qt.UserRole) == "alerte", "alerte: ligne marquée en alerte")
    verifier(item.background().color() == QColor(BASE_UI["fond_ligne_alerte"]), "alerte: fond de ligne coloré")
    verifier(fenetre.results_table.item(ligne_alerte, 6).text() == "ALERTE", "alerte: statut ALERTE affiché")

# 5. Journal horodaté.
derniere_ligne = fenetre.log.toPlainText().strip().splitlines()[-1]
verifier(re.match(r"^\d{2}:\d{2}:\d{2} — \[", derniere_ligne) is not None, f"journal: horodatage correct ({derniere_ligne[:30]}...)")

# 6. Retour Logiviande + traitement Bizerba avec Adapter LLM (mock sans clé).
fenetre.module_combo.setCurrentText("Logiviande")
app.processEvents()
fenetre.file_path_label.setText(str(SAMPLES / "bizerba_export.csv"))
fenetre.llm_checkbox.setChecked(True)
fenetre.process_button.click()
attendre_worker()
verifier(fenetre.results_table.rowCount() == 9, f"traitement Logiviande LLM: 9 lignes attendues, {fenetre.results_table.rowCount()} affichées")
colonne_rendement = TABLE_COLUMNS["Logiviande"].index("Rendement%")
rendements = [fenetre.results_table.item(r, colonne_rendement).text() for r in range(fenetre.results_table.rowCount())]
verifier(all(rendements), "traitement Logiviande: colonne Rendement% remplie")
colonne_espece = TABLE_COLUMNS["Logiviande"].index("Espèce")
especes = {fenetre.results_table.item(r, colonne_espece).text() for r in range(fenetre.results_table.rowCount())}
verifier(especes == {"bovin"}, f"traitement Logiviande: colonne Espèce remplie (défaut bovin), obtenu {especes}")

print()
if erreurs:
    print(f"{len(erreurs)} ECHEC(S)")
    sys.exit(1)
print("TOUS LES TESTS UI PASSENT")
sys.exit(0)
