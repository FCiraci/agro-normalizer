# agro-normalizer

`agro-normalizer` est le nom de travail d'un moteur de normalisation de flux
heterogenes pour l'agro-alimentaire. Le projet sert a demontrer une idee simple :
construire un seul moteur generique capable d'absorber plusieurs formats de
fichiers, de les normaliser vers un modele commun, puis de calculer des indicateurs
et des alertes metier.

La demonstration cible deux cas proches de situations reelles chez Agorinfo :
Logiviande pour les pesees et Silos pour les apports cerealiers. L'objectif n'est
pas de coder deux applications separees, mais de prouver qu'un meme socle technique
peut etre reutilise sur plusieurs metiers.

## Contexte

Dans un SI agro-alimentaire, les donnees arrivent rarement dans un format propre et
unique. Les balances, sites de collecte, logiciels historiques et exports CSV ou
Excel produisent des fichiers differents selon les marques, les clients et les
habitudes terrain.

Le projet part de cette contrainte : plutot que de developper un import specifique
pour chaque source, on isole la complexite dans un moteur commun :

- lecture d'un fichier entrant ;
- adaptation du format source ;
- normalisation vers un modele metier commun ;
- calcul d'indicateurs ;
- detection d'anomalies ;
- exposition des resultats via une API ;
- visualisation dans une application desktop de type logiciel industriel.

L'interet pour un editeur qui possede plusieurs logiciels metier est la
reutilisabilite. Le meme principe peut servir Logiviande, Silos, LSA, Comptinnov ou
d'autres modules, sans repartir de zero a chaque nouveau flux.

## Idee centrale

Le coeur du projet est un moteur generique :

```text
Adapter -> Normalisation -> Calculs metier -> Detection d'anomalies -> API -> GUI desktop
```

Le point important est que le moteur est pense pour etre reutilisable. Logiviande et
Silos ne doivent pas etre deux implementations independantes, mais deux preuves que
le meme pipeline peut traiter des metiers differents.

Un element differenciant est prevu dans l'interface : chaque normalisation pourra
etre comparee avec deux strategies d'adaptation affichees cote a cote :

- un mapping ecrit en dur, rapide et fiable pour un format connu, mais fragile si le
  format change ;
- un mapping pilote par LLM, plus souple pour analyser un format jamais vu ou mal
  documente.

Cette comparaison permet de montrer a la fois une approche industrielle classique
et une approche IA plus adaptable.

## Modules fonctionnels cibles

### Module 1 - Logiviande : pesees

Le cas Logiviande simule l'import de fichiers de pesee venant de balances de marques
differentes, par exemple Bizerba, Dini Argeo ou Multivac. Chaque marque peut exporter
des colonnes, libelles, encodages ou unites differents.

Le moteur doit normaliser ces fichiers vers un modele commun de bon de pesee, avec
des informations comme le lot, le poids carcasse, le poids decoupe et le classement
EUROP.

Une fois les donnees normalisees, le moteur calcule le rendement :

```text
rendement = poids decoupe / poids carcasse * 100
```

Une alerte peut ensuite etre remontee si le rendement sort d'une plage normale.

### Module 2 - Silos : apports cerealiers

Le cas Silos simule l'import d'apports cerealiers depuis plusieurs sites de collecte.
La aussi, les fichiers sources peuvent varier selon le site, le logiciel ou la
procedure locale.

Le moteur doit normaliser les donnees vers un modele commun d'apport cerealier, avec
des informations comme le site, la cereale, le poids net et le taux d'humidite.

Une fois les donnees normalisees, le moteur calcule notamment une moyenne ponderee
par tonnage :

```text
moyenne ponderee = somme(taux humidite * poids net) / somme(poids net)
```

Une alerte peut etre remontee si un taux d'humidite depasse le seuil de conservation.

## Architecture

L'architecture cible separe les responsabilites entre trois couches principales :

```text
Python
ETL, adapters, normalisation, detection d'anomalies, option LLM
        |
        | HTTP / JSON
        v
Java / Spring Boot
API REST, orchestration applicative, persistance
        |
        | HTTP / JSON
        v
PySide6
Application desktop, import, previsualisation, journal machine
```

Le module Python porte la logique data : lecture des fichiers, mapping des colonnes,
normalisation, calculs et eventuellement interpretation assistee par LLM.

Le module Java Spring Boot porte la partie API et architecture applicative. A terme,
il pourra exposer des routes comme :

- `POST /lots` pour recevoir un lot de donnees normalisees ;
- `GET /lots/{id}` pour consulter un lot ;
- `GET /lots/alertes` pour consulter les alertes detectees.

Le module desktop PySide6 porte l'experience utilisateur locale. Ce n'est pas une
interface web : il s'agit d'une vraie fenetre de logiciel, pensee comme une console
operateur industrielle simple, avec un panneau d'import, une table de
previsualisation et un journal machine.

## Modules du depot

```text
agro-normalizer/
  python/
    adapters/
    models/
    tests/
    requirements.txt
    README.md
  java/
    pom.xml
    src/main/java/com/agronormalizer/
      controller/
      model/
      repository/
      LotsApiApplication.java
  desktop/
    app.py
  data/
    samples/
  README.md
```

### `python/`

Contiendra le moteur ETL et IA :

- adapters de fichiers sources ;
- modeles normalises ;
- calculs metier ;
- detection d'anomalies ;
- tests unitaires.

Le fichier `python/requirements.txt` contient aussi la dependance PySide6 pour
l'application desktop.

### `java/`

Contient le projet Maven Spring Boot `lots-api`, avec le groupId
`com.agronormalizer` et Java 21.

Pour l'instant, le module ne contient qu'une application Spring Boot minimale qui
compile et demarre. Les packages `model`, `repository` et `controller` sont presents
pour preparer l'architecture, mais ils ne contiennent pas encore de classes metier.

### `desktop/`

Contient l'application PySide6. L'interface actuelle est une maquette executable de
console operateur : sobre, industrielle et facile a etendre, plutot qu'une page web.

Elle ne lance pas de serveur et ne depend pas d'un navigateur.

### `data/samples/`

Recevra les faux fichiers de pesee et d'apports cerealiers utilises pour demontrer
le fonctionnement du moteur.

## Etat actuel

Le depot contient uniquement le squelette technique et une premiere GUI desktop :

- arborescence Python ;
- projet Spring Boot Maven minimal ;
- application PySide6 minimale ;
- dossier de samples ;
- configuration `.gitignore` ;
- documentation initiale.

Aucune classe metier n'est encore implementee. Il n'y a pas encore de modele
`BonDePesee`, de modele `ApportCereale`, d'adapter, de repository, de controller ou
d'endpoint REST.

## Comment lancer

### Installer les dependances Python

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r python/requirements.txt
```

### Application desktop PySide6

```bash
python desktop/app.py
```

### API Spring Boot

```bash
cd java
mvn spring-boot:run
```

### Build Java

```bash
cd java
mvn clean install
```

## Vision

Le projet doit montrer trois competences dans un meme fil conducteur :

- Python pour la partie ETL, data et IA ;
- Java / Spring Boot pour l'API, la persistance et l'architecture applicative ;
- PySide6 pour une vraie application desktop de supervision.

Le resultat attendu est un prototype qui prouve une logique systeme : des donnees
heterogenes entrent, un modele commun sort, des alertes sont calculees, et l'ensemble
est visible dans une interface de supervision locale.
