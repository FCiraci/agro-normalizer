from __future__ import annotations

import csv
from pathlib import Path


def _decoder_texte_csv(contenu_brut: bytes) -> str:
	for encodage in ("utf-8-sig", "utf-8", "latin-1"):
		try:
			return contenu_brut.decode(encodage)
		except UnicodeDecodeError:
			continue

	raise UnicodeDecodeError(
		"utf-8",
		contenu_brut,
		0,
		len(contenu_brut),
		"Impossible de decoder le fichier CSV avec utf-8 ou latin-1.",
	)


def _lire_ligne_csv(ligne: str) -> list[str]:
	lecteur = csv.reader([ligne])
	return next(lecteur)


def lire_csv(chemin_fichier: str | Path) -> list[dict[str, str]]:
	chemin = Path(chemin_fichier)
	if not chemin.exists() or chemin.stat().st_size == 0:
		return []

	contenu = _decoder_texte_csv(chemin.read_bytes())
	lignes = contenu.splitlines()
	if not lignes:
		return []

	try:
		entetes = [colonne.strip() for colonne in _lire_ligne_csv(lignes[0])]
	except csv.Error:
		return []

	if not any(entetes):
		return []

	donnees: list[dict[str, str]] = []

	for ligne in lignes[1:]:
		if not ligne.strip():
			continue

		# Une ligne avec un nombre impair de guillemets est vraisemblablement corrompue.
		if ligne.count('"') % 2 != 0:
			continue

		try:
			valeurs = _lire_ligne_csv(ligne)
		except csv.Error:
			continue

		if len(valeurs) != len(entetes):
			continue

		donnees.append(
			{
				entete: valeur.strip()
				for entete, valeur in zip(entetes, valeurs, strict=True)
			}
		)

	return donnees
