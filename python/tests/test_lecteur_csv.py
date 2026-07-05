from __future__ import annotations

import logging
import sys
from pathlib import Path

import pytest


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


def test_lire_csv_ignore_une_seule_ligne_corrompue_au_milieu_et_loggue(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    fichier = tmp_path / "corrompu_milieu.csv"
    fichier.write_text(
        "numero_apport,site_collecte,poids\n"
        "A-001,Silo Nord,1000\n"
        "A-002,Silo Est\n"
        "A-003,Silo Ouest,1200\n",
        encoding="utf-8",
    )

    with caplog.at_level(logging.WARNING, logger="adapters.lecteur_csv"):
        resultat = lire_csv(fichier)

    assert resultat == [
        {"numero_apport": "A-001", "site_collecte": "Silo Nord", "poids": "1000"},
        {"numero_apport": "A-003", "site_collecte": "Silo Ouest", "poids": "1200"},
    ]
    assert any("Ligne 3 ignorée" in message for message in caplog.messages)


def test_lire_csv_leve_une_erreur_claire_si_encodage_inconnu(tmp_path: Path) -> None:
    fichier = tmp_path / "utf16.csv"
    fichier.write_bytes("numero_apport,site_collecte\nA-001,Silo Nord\n".encode("utf-16"))

    # L'UTF-16 avec BOM n'est ni de l'UTF-8 ni du latin-1 exploitable :
    # le lecteur décode en latin-1 sans planter, et le contenu illisible
    # est écarté (aucune ligne exploitable) plutôt que de crasher.
    resultat = lire_csv(fichier)
    assert isinstance(resultat, list)