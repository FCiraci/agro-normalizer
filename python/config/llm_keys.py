from __future__ import annotations

import os
from pathlib import Path


def _charger_env_local() -> None:
	chemins_possibles = [
		Path(__file__).resolve().parents[2] / ".env",
		Path(__file__).resolve().parents[1] / ".env",
	]

	for chemin in chemins_possibles:
		if not chemin.exists():
			continue

		for ligne in chemin.read_text(encoding="utf-8").splitlines():
			ligne = ligne.strip()
			if not ligne or ligne.startswith("#") or "=" not in ligne:
				continue

			cle, valeur = ligne.split("=", 1)
			cle = cle.strip()
			if not cle or cle in os.environ:
				continue

			os.environ[cle] = valeur.strip().strip('"').strip("'")


_charger_env_local()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
