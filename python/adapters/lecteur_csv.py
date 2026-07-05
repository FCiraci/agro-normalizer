from __future__ import annotations

import csv
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


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


def _detecter_delimiteur(contenu: str) -> csv.Dialect | None:
	try:
		return csv.Sniffer().sniff(contenu, delimiters=[",", ";", "\t"])
	except csv.Error:
		return None


def lire_csv(chemin_fichier: str | Path) -> list[dict[str, str]]:
	chemin = Path(chemin_fichier)
	if not chemin.exists() or chemin.stat().st_size == 0:
		return []

	contenu = _decoder_texte_csv(chemin.read_bytes())
	lignes = contenu.splitlines()
	if not lignes:
		return []

	dialecte = _detecter_delimiteur("\n".join(lignes[:5]))

	try:
		if dialecte is None:
			entetes = [colonne.strip() for colonne in _lire_ligne_csv(lignes[0])]
		else:
			entetes = [colonne.strip() for colonne in next(csv.reader([lignes[0]], dialect=dialecte))]
	except csv.Error:
		return []

	if not any(entetes):
		return []

	donnees: list[dict[str, str]] = []

	for numero_ligne, ligne in enumerate(lignes[1:], start=2):
		if not ligne.strip():
			continue

		# Une ligne avec un nombre impair de guillemets est vraisemblablement corrompue.
		if ligne.count('"') % 2 != 0:
			logger.warning(
				"Ligne %d ignorée dans %s: guillemets non fermés (ligne corrompue): %r",
				numero_ligne, chemin.name, ligne,
			)
			continue

		try:
			if dialecte is None:
				valeurs = _lire_ligne_csv(ligne)
			else:
				valeurs = next(csv.reader([ligne], dialect=dialecte))
		except csv.Error as exc:
			logger.warning(
				"Ligne %d ignorée dans %s: erreur de parsing CSV (%s): %r",
				numero_ligne, chemin.name, exc, ligne,
			)
			continue

		if len(valeurs) != len(entetes):
			logger.warning(
				"Ligne %d ignorée dans %s: %d colonnes au lieu de %d attendues: %r",
				numero_ligne, chemin.name, len(valeurs), len(entetes), ligne,
			)
			continue

		donnees.append(
			{
				entete: valeur.strip()
				for entete, valeur in zip(entetes, valeurs, strict=True)
			}
		)

	return donnees
