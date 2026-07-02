from __future__ import annotations

import sys
from pathlib import Path


PYTHON_DIR = Path(__file__).resolve().parents[1]
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from adapters.lecteur_csv import lire_csv


def test_lire_csv_retourne_une_liste_vide_pour_un_fichier_vide(tmp_path: Path) -> None:
    fichier = tmp_path / "vide.csv"
    fichier.write_text("", encoding="utf-8")

    assert lire_csv(fichier) == []


def test_lire_csv_decode_utf8_et_retourne_des_dicts(tmp_path: Path) -> None:
    fichier = tmp_path / "utf8.csv"
    fichier.write_text(
        "numero_apport,site_collecte\nA-001,Silo Nord\nA-002,Silo Est\n",
        encoding="utf-8",
    )

    assert lire_csv(fichier) == [
        {"numero_apport": "A-001", "site_collecte": "Silo Nord"},
        {"numero_apport": "A-002", "site_collecte": "Silo Est"},
    ]


def test_lire_csv_decode_latin1_et_ignore_une_ligne_corrompue(tmp_path: Path) -> None:
    fichier = tmp_path / "latin1.csv"
    contenu = (
        "numero_apport,site_collecte\n"
        "A-001,Silo Nord\n"
        'A-002,"Silo Est\n'
        "A-003,Silo Ouest\n"
        "A-004,Silo \xe9tang\n"
    )
    fichier.write_bytes(contenu.encode("latin-1"))

    assert lire_csv(fichier) == [
        {"numero_apport": "A-001", "site_collecte": "Silo Nord"},
        {"numero_apport": "A-003", "site_collecte": "Silo Ouest"},
        {"numero_apport": "A-004", "site_collecte": "Silo étang"},
    ]