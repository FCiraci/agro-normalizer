# RAPPORT DE TESTS — agro-normalizer

Audit complet et test end-to-end réalisé le 2026-07-05.
Ce fichier est mis à jour au fur et à mesure de l'audit.

---

## 1. Environnement

| Vérification | Statut | Détail |
|---|---|---|
| Python | ✅ OK | Python 3.11.9 |
| venv (`.venv/`) | ✅ OK | Présent et fonctionnel |
| `pip install -r python/requirements.txt` | ✅ OK | Installation sans erreur |
| Java 21 | 🔧 CORRIGÉ | Seul JDK 17 était installé (le pom exige Java 21). Installation portable de **Temurin JDK 21.0.11** dans `C:\Users\Furkan\tools\jdk-21.0.11+10` |
| Maven | 🔧 CORRIGÉ | Maven absent du système. Installation portable de **Maven 3.9.9** dans `C:\Users\Furkan\tools\apache-maven-3.9.9` |
| `mvn clean install` | ✅ OK | BUILD SUCCESS avec JDK 21 — 15/15 tests d'intégration passent, jar produit |
| Dépendances pom.xml | 🔧 CORRIGÉ | `spring-boot-starter-data-jpa` + `h2` étaient déclarés mais **jamais utilisés** (le repository est une Map en mémoire) : retirés du pom |

> Pour compiler/lancer le module Java, définir `JAVA_HOME=C:\Users\Furkan\tools\jdk-21.0.11+10` et utiliser `C:\Users\Furkan\tools\apache-maven-3.9.9\bin\mvn.cmd` (ou ajouter ces chemins au PATH).

## 2. Tests unitaires Python

- `pytest python/tests/ -v` : **28/28 tests passent** avant modifications.

### Bugs trouvés et corrigés

| # | Fichier | Bug | Correction |
|---|---|---|---|
| B1 | `python/adapters/adapter_bizerba.py`, `adapter_dini_argeo.py`, `adapter_multivac.py` | `_champ_obligatoire()` loggue un champ manquant mais **ne lève pas d'exception** (contrairement aux adapters Site A/B/C). Une ligne sans `Classe` ou `Balance` passait silencieusement avec une valeur vide. | Ajout du `raise ValueError` après le log, aligné sur les adapters Silos. |
| B2 | `python/pipeline.py` | `_verifier_rendement_logiviande()` testait `hasattr(objet, "calculerRendement")` (nom **Java** camelCase) au lieu de `calculer_rendement` (nom Python). Le contrôle « rendement > 100 % » ne s'exécutait **jamais**. | Appel corrigé vers `calculer_rendement()`. |
| B3 | `python/adapters/adapter_factory.py` | La détection Site B utilisait `"est" in source`. Or « Silo **Ouest** » contient « est » : un flux du site Ouest était routé vers l'adapter Site B. | Exclusion de « ouest » de la règle Site B + test de non-régression. |
| B4 | `python/adapters/lecteur_csv.py` | Les lignes corrompues (guillemets non fermés, nombre de colonnes incorrect) étaient ignorées **silencieusement**, sans message de log. | Ajout de `logger.warning` explicite avec numéro de ligne et raison. |

### Cas limites (ajoutés s'ils manquaient)

| Cas | Statut |
|---|---|
| rendement = seuil min exact (35.0 bovin) | ✅ Existait |
| rendement = seuil max exact (60.0 bovin) | 🔧 AJOUTÉ |
| poids_carcasse_kg = 0 → ValueError propre | ✅ Existait |
| poids_decoupe_kg > poids_carcasse_kg (rendement > 100 %) détecté | 🔧 AJOUTÉ |
| Fichier CSV vide | ✅ Existait |
| CSV avec une seule ligne corrompue au milieu | ✅ Existait (renforcé) |
| Encodage non-UTF8 (latin-1) | ✅ Existait |

## 3. Adapters (statique et LLM)

Les fichiers `site_a_export.csv`, `site_b_export.csv`, `site_c_export.csv` étaient **absents** de `data/samples/`
alors que les adapters existaient : ils ont été créés, avec des lignes corrompues volontaires
(colonnes manquantes, guillemets non fermés, poids vide/négatif/nul, humidité `N/A`).

Audit exécuté via `python/audit_adapters.py` (POST HTTP neutralisé) — comptages vérifiés :

| Fichier | Lignes traitées | Normalisées | Rejetées (avec log explicite) | Statique | LLM mock |
|---|---|---|---|---|---|
| bizerba_export.csv | 10 | 9 | 1 (Pds_Decoupe vide) | ✅ | ✅ |
| dini_argeo_export.csv | 10 | 10 | 0 | ✅ | ✅ |
| multivac_export.csv | 10 | 9 | 1 (poids découpe négatif) | ✅ | ✅ |
| site_a_export.csv | 9 (+1 droppée par lecteur_csv : 5 colonnes/7) | 8 | 1 (Poids_Net vide) | ✅ | ✅ |
| site_b_export.csv | 7 (+1 droppée par lecteur_csv : guillemets) | 6 | 1 (poids négatif) | ✅ | ✅ |
| site_c_export.csv | 7 | 5 | 2 (humidité N/A, poids nul) | ✅ | ✅ |

- Aucune ligne corrompue ne fait crasher le pipeline ; chacune produit un `logger.warning` explicite. ✅
- Le JSON produit (to_dict) respecte le schéma BonDePesee / ApportCereale pour 100 % des lignes normalisées. ✅

### Bugs trouvés et corrigés

| # | Fichier | Bug | Correction |
|---|---|---|---|
| B5 | `python/adapters/adapter_llm.py` | Le mode mock ne connaissait que les en-têtes Bizerba et Dini Argeo (2 mappings en dur, avec un try/except en cascade) : il **plantait sur Multivac** et ne supportait pas du tout le schéma Silos/ApportCereale. | Réécriture : le mock déduit le mapping depuis les en-têtes via une table de synonymes (simulation déterministe du LLM), support du paramètre `module="logiviande"/"silos"` avec schéma et prompt système dédiés. Échec **explicite** si un en-tête est inconnu (pas de try/except masquant). |
| B6 | `python/pipeline.py` | `use_llm=True` sur le module Silos retombait silencieusement sur l'adapter statique (l'AdapterLLM ne gérait pas les apports). | `_resoudre_adapter` instancie désormais `AdapterLLM(module=module)` pour les deux modules. |

## 4. API Spring Boot

L'application démarre sans exception (`Started LotsApiApplication in 3.5 s`).
Tous les endpoints ont été testés **deux fois** : via `curl` sur le serveur réel, et via
15 tests d'intégration MockMvc ajoutés dans `java/src/test/java/.../ApiIntegrationTest.java`
(exécutés par `mvn test`).

| Cas testé | /lots | /apports | Attendu | Obtenu |
|---|---|---|---|---|
| POST body valide | ✅ | ✅ | 201 + objet créé | 201 + `{id, alerte, [rendement_pct], objet}` |
| POST champ manquant | ✅ | ✅ | 400 | 400 + message explicite |
| POST poids négatif | ✅ | ✅ | 422 | 422 + message explicite |
| POST JSON malformé | ✅ | ✅ | 400 | 400 « Body JSON malformé » |
| GET /{id} existant | ✅ | ✅ | 200 | 200 |
| GET /{id} inexistant | ✅ | ✅ | 404 (pas d'exception brute) | 404 + `{"error": ...}` |
| GET /alertes base vide | ✅ | ✅ | 200 + `[]` (jamais 404) | 200 + `[]` |
| GET /alertes avec alertes | ✅ | ✅ | 200 + liste filtrée | 200 + liste filtrée correcte |

### Bugs / manques trouvés et corrigés

| # | Fichier | Problème | Correction |
|---|---|---|---|
| B7 | `java/` (tout le module) | **Le miroir `/apports` (Silos) n'existait pas du tout** : seul `/lots` était implémenté, alors que le pipeline Python poste sur `/apports`. | Création de `Apport`, `ApportDto`, `ApportMapper`, `ApportRepository(-EnMemoire)`, `ApportService`, `ApportController` en miroir exact de la pile Lot (201/400/422/200/404, alertes humidité par céréale). |
| B8 | `java/src/main/resources/application.properties` (créé) | **Incompatibilité de contrat JSON** : Python envoie du snake_case (`numero_lot`, `poids_carcasse_kg`), les DTO Java attendaient du camelCase → chaque POST réel du pipeline aurait donné 400 « Champ manquant ». Le test d'intégration Python ne le voyait pas car il *mockait* l'API. | Ajout de `spring.jackson.property-naming-strategy=SNAKE_CASE`. |
| B9 | `LotController.java` | Pas de `GET /lots` (liste) pour vérifier les insertions ; réponse POST sans l'objet créé. | Ajout de `GET /lots` + `GET /apports`, et l'objet créé est retourné dans la réponse 201. |
| B10 | `LotRepositoryEnMemoire.java` | `HashMap` non thread-safe utilisé par un contrôleur web concurrent. | Remplacé par `ConcurrentHashMap` (idem pour le nouveau repo Apport). |

## 5. Pipeline bout-en-bout Python → Java

Exécuté via `python/audit_e2e.py` contre l'API réelle (serveur lancé en arrière-plan) :

- **Mode statique** : 47 objets normalisés et POSTés (9+10+9 lots, 8+6+5 apports), chacun **relu avec succès via `GET /{id}` juste après le POST**. ✅
- **Mode LLM mock** (`use_llm=True`, sans clé API) : mêmes comptages, mêmes relectures. ✅
- `GET /lots/alertes` → 200 + 29 alertes (tous les lots à rendement ~72–76 % sont hors de la plage bovin 35–60 % : cohérent avec les seuils). ✅
- `GET /apports/alertes` → 200 + 5 alertes, exactement les apports au-dessus des seuils d'humidité (16.2 % blé, 15.1 % orge, 15.8/14.9/16.0 % maïs). ✅
- **Serveur Java coupé en plein run** : le pipeline **ne plante pas et n'échoue pas silencieusement** — chaque ligne retourne `succes=False` avec `erreur_eventuelle="API Java injoignable: ..."` et un `logger.error` explicite. ✅

## 6. Interface PySide6

Testée via `desktop/test_ui_smoke.py` (pilotage programmatique des widgets, 15 vérifications) :

| Vérification | Statut |
|---|---|
| Démarrage sans exception (`desktop/app.py` lancé réellement, vivant après 6 s) | ✅ |
| Changement QComboBox Logiviande/Silos → colonnes du QTableWidget changées | ✅ |
| Changement de module → thème de couleur changé (rouge #7A0E0E / brun #6B4226) | ✅ |
| Bouton « Traiter le fichier » → `run_pipeline()` réel + tableau peuplé (6 lignes site_b, 9 lignes bizerba en mode LLM) | 🔧 CORRIGÉ puis ✅ |
| Lignes en alerte colorées (fond `#F1D7D7` + statut ALERTE) | ✅ |
| Journal QTextEdit incrémenté à chaque traitement, horodatage `HH:MM:SS` | ✅ |
| Pas de freeze UI pendant l'appel API | 🔧 CORRIGÉ puis ✅ |

### Bugs trouvés et corrigés

| # | Fichier | Problème | Correction |
|---|---|---|---|
| B11 | `desktop/app.py` | Le bouton « Traiter le fichier » était un **stub** (« Bloc de traitement simulé ») : il loggait un message mais n'appelait jamais `run_pipeline()`, ne remplissait jamais le tableau. | `_process_file` lance désormais le pipeline réel et peuple le tableau (colonnes selon le module, rendement calculé, statut OK/ALERTE). |
| B12 | `desktop/app.py` | Aucun threading : un appel API (10 s de timeout par ligne si serveur coupé) aurait **gelé l'UI**. | Ajout de `PipelineWorker(QThread)` avec signaux `termine`/`echec` ; bouton désactivé pendant le run puis réactivé. |

Note : la sélection par QFileDialog est branchée (`getOpenFileName`, filtre CSV) mais la boîte de
dialogue native ne peut pas être automatisée — voir « Risques restants ».

## 7. Moyenne pondérée (Silos)

Vérifiée par tests unitaires ajoutés dans `test_calculateur_silos.py` :

- Jeu 5 000 kg @10 % / 20 000 kg @12 % / 45 000 kg @16 % → moyenne pondérée **14,43 %**
  (moyenne simple : 12,67 %) : bien tirée vers l'apport le plus lourd. ✅
- Liste vide → `ValueError("La liste des apports ne peut pas être vide.")`. ✅
- Somme des poids nulle (y compris plusieurs apports à 0 kg) → `ValueError(...nulle...)`. ✅

## 8. Cohérence globale et nettoyage

| Vérification | Statut | Détail |
|---|---|---|
| Seuils rendement Python vs Java | ✅ OK | bovin 35–60 %, porc 60–85 % identiques des deux côtés (`bons_de_pesee.py` ↔ `Lot.java`) |
| Seuils humidité Python vs Java | ✅ OK | blé 15 / maïs 14 / orge 14,5 identiques (`apport_cereale.py` ↔ `Apport.java`, créé avec les mêmes valeurs) |
| Secrets en dur | ✅ OK | Aucune clé dans le code (grep sk-ant/pplx/api_key) ; tout passe par `os.getenv` + `.env` (gitignoré) ; `.env.example` fourni |
| `.gitignore` | 🔧 CORRIGÉ | `.env.example` était **ignoré par git** alors qu'il doit être versionné : ligne retirée |
| README : ordre de lancement | 🔧 CORRIGÉ | Section « Comment lancer » réécrite : Java d'abord, puis Python/desktop, avec chemins JDK 21/Maven ; section « Etat actuel » obsolète (« aucune classe métier ») mise à jour |
| README : section tests | 🔧 AJOUTÉ | Commandes pytest, `mvn test` et test de fumée UI documentées ; `python/README.md` (qui était vide) complété |

---

## Synthèse des bugs corrigés

| # | Fichier | Nature |
|---|---|---|
| B1 | `adapter_bizerba.py`, `adapter_dini_argeo.py`, `adapter_multivac.py` | Champ obligatoire manquant loggé mais non rejeté (pas de `raise`) |
| B2 | `pipeline.py` | Contrôle rendement > 100 % jamais exécuté (`calculerRendement` au lieu de `calculer_rendement`) |
| B3 | `adapter_factory.py` | « Silo Ouest » routé vers l'adapter Site B (« ouest » contient « est ») |
| B4 | `lecteur_csv.py` | Lignes corrompues ignorées sans aucun log |
| B5 | `adapter_llm.py` | Mock limité à 2 formats (plantait sur Multivac), pas de support du schéma ApportCereale |
| B6 | `pipeline.py` | `use_llm=True` ignoré silencieusement pour le module Silos |
| B7 | `java/` | Miroir `/apports` totalement absent |
| B8 | `application.properties` | Contrat JSON incompatible Python (snake_case) ↔ Java (camelCase) : tout POST réel aurait renvoyé 400 |
| B9 | `LotController.java` | Pas de GET liste ; POST ne renvoyait pas l'objet créé |
| B10 | `LotRepositoryEnMemoire.java` | HashMap non thread-safe |
| B11 | `desktop/app.py` | Traitement simulé : `run_pipeline()` jamais appelé, tableau jamais rempli |
| B12 | `desktop/app.py` | Aucun threading : freeze UI garanti pendant les appels HTTP |

Corrections d'environnement : installation portable JDK 21 (Temurin 21.0.11) et Maven 3.9.9 dans
`C:\Users\Furkan\tools\` ; retrait des dépendances `spring-boot-starter-data-jpa` + `h2` inutilisées.

Fichiers ajoutés : `data/samples/site_{a,b,c}_export.csv`, `java/.../Apport*.java` (6 classes),
`ApiIntegrationTest.java`, `application.properties`, `python/audit_adapters.py`, `python/audit_e2e.py`,
`python/tests/test_adapter_balances.py`, `desktop/test_ui_smoke.py`.

---

## Mises à niveau post-audit (2ᵉ passe)

À la demande, les points « à surveiller » actionnables ont été traités :

| # | Upgrade | Détail |
|---|---|---|
| U1 | **Champ `espece` par lot, bout-en-bout** | Python : `BonDePesee.espece` (défaut `bovin`, inclus dans `to_dict()`), `est_en_alerte()`/`ecart_vs_standard()` utilisent l'espèce du lot sans argument ; adapters Bizerba/Dini/Multivac lisent une colonne espèce **optionnelle** (`Espece`/`species`/`ESPECE`) validée contre les seuils ; AdapterLLM la mappe si présente (champ facultatif, pas d'échec si absent). Java : `espece` dans `LotDto`/`Lot` (défaut `bovin`), validation → **422 « Espèce inconnue »**, alertes évaluées avec l'espèce du lot (`/lots/alertes` et réponse POST). UI : colonne « Espèce » dans le tableau Logiviande. Vérifié en réel : lot porc à 73 % → `alerte=false` ; même rendement en bovin → alerte. |
| U2 | **Spring Boot 3.3.1 → 3.5.3** (dernière 3.x sur Maven Central) | `mvn clean install` : BUILD SUCCESS, **17/17** tests d'intégration (15 + 2 nouveaux tests espèce). Serveur relancé et re-testé en réel. |
| U3 | **JAVA_HOME + PATH utilisateur** | `JAVA_HOME` (utilisateur) → JDK 21 portable ; `C:\Users\Furkan\tools\apache-maven-3.9.9\bin` et `...\jdk-21.0.11+10\bin` ajoutés au `Path` utilisateur. `mvn` et `java` 21 sont disponibles dans tout **nouveau** terminal (les terminaux déjà ouverts doivent être relancés). |
| U4 | **requirements.txt épinglé** | `PySide6==6.11.1`, `pytest==9.1.1`, `requests==2.34.2`, `responses==0.26.2` (reproductibilité). |

## État final des suites de tests (après upgrades)

- `pytest python/tests/ -v` : **50/50 passent** (28 avant audit → 46 après audit → 50 avec les tests espèce).
- `mvn clean install` (JDK 21, Spring Boot 3.5.3) : **BUILD SUCCESS, 17/17 tests d'intégration**.
- `desktop/test_ui_smoke.py` : **16/16 vérifications passent** (API réelle, colonne Espèce incluse).
- `python/audit_e2e.py` : 47 objets par mode POSTés et relus via GET, alertes cohérentes.
- Vérifications curl en réel : lot porc 73 % → 201 + `alerte=false` ; espèce inconnue → 422 ; sans espèce → défaut `bovin`.

## Risques restants (vérification manuelle recommandée)

1. **Rendu visuel PySide6** : les couleurs, la lisibilité des thèmes et le comportement du
   QFileDialog natif (ouverture, filtre `*.csv`) ont été vérifiés programmatiquement mais pas
   visuellement. Lancer `python desktop/app.py` et dérouler un traitement pour valider à l'œil.
2. **Adapter LLM en mode réel** (`ANTHROPIC_API_KEY` renseignée) : seul le mode mock a été testé
   automatiquement (pas d'appel API facturé pendant l'audit). Le parsing de la réponse LLM est
   couvert par des tests (JSON invalide, mapping incomplet), mais un run réel de bout en bout
   reste à faire une fois une clé fournie.
3. **Persistance en mémoire** : les données sont perdues à chaque redémarrage de l'API (Map en
   mémoire, pas de base). C'était le design d'origine ; à garder en tête pour la démo.
4. **Espèce dans les échantillons** : les CSV de `data/samples/` ne portent pas de colonne espèce
   → tous les lots restent en `bovin` par défaut (rendements ~73 % donc en alerte). Ajouter une
   colonne `Espece`/`species`/`ESPECE` aux fichiers sources suffit, toute la chaîne la prend
   désormais en compte.
