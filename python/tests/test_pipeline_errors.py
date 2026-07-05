from __future__ import annotations

import sys
from pathlib import Path

import pytest
import requests


PYTHON_DIR = Path(__file__).resolve().parents[1]
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

import pipeline


def test_poster_objet_rejette_une_reponse_non_json(monkeypatch: pytest.MonkeyPatch) -> None:
    class FauxResponse:
        ok = True
        status_code = 201
        text = "ok"
        reason = "Created"

        def json(self):
            raise ValueError("not json")

    monkeypatch.setattr(pipeline.requests, "post", lambda *args, **kwargs: FauxResponse())

    with pytest.raises(ValueError, match="Réponse API non-JSON"):
        pipeline._poster_objet("http://localhost:8080/lots", {"foo": "bar"})
