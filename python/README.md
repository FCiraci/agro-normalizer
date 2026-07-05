# Module Python

Moteur ETL du projet : lecture CSV, adapters (statiques et LLM), modeles
metier normalises, calculs et envoi vers l'API Java.

- `adapters/` : lecteur CSV robuste + un adapter par format source
  (Bizerba, Dini Argeo, Multivac, Sites A/B/C) + `adapter_llm.py`
  (mapping pilote par LLM, mode mock deterministe sans cle API).
- `models/` : `BonDePesee` (Logiviande), `ApportCereale` et
  `CalculateurSilos` (Silos), avec seuils d'alerte metier.
- `pipeline.py` : orchestre lecture -> adaptation -> validation -> POST
  vers `http://localhost:8080/lots` ou `/apports`.
- `audit_adapters.py` : verifie la normalisation sur tous les samples sans API.
- `audit_e2e.py` : verifie le bout-en-bout avec l'API Java demarree.

## Tests

```powershell
..\.venv\Scripts\python.exe -m pytest tests/ -v
```
