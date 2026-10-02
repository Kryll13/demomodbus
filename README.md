# Modbus TCP en Python : serveur, client et simulation

Travail dirigé réalisé avec Python, la bibliothèque `pymodbus` (version 3.15), `uv` et Git.
L'objectif est de comprendre le modèle mémoire Modbus en le manipulant : décrire un appareil,
l'exposer sur le réseau, puis lire et écrire ses données avec un client.

## Objectifs du travail

À l'issue de ce travail, vous devez être capable de :

1. décrire la mémoire d'un appareil Modbus à l'aide des quatre sigles CO, DI, HR et IR ;
2. démarrer un serveur Modbus TCP avec `pymodbus` et connaître sa carte mémoire ;
3. lire et écrire des données avec un client Modbus TCP ;
4. faire évoluer une valeur simulée dans le temps et la publier dans les registres du serveur ;
5. utiliser `uv` pour créer l'environnement d'exécution et `Git` pour conserver une trace des modifications.

## Dénomination de la mémoire Modbus

Un appareil Modbus expose quatre blocs de données. Ils sont désignés ci-après par les sigles **CO**, **DI**, **HR** et **IR**, qui sont ceux employés par les noms de fonctions et de méthodes de `pymodbus` :

| Sigle | Dénomination anglaise | Traduction française | Accès | Granularité d'une adresse |
|-------|-----------------------|----------------------|-------|--------------------------|
| CO | Coils | Bobines (sorties) | lecture / écriture | 1 bit |
| DI | Discrete Inputs | Entrées discrètes | lecture seule | 1 bit |
| HR | Holding Registers | Registres de maintien | lecture / écriture | 1 registre de 16 bits |
| IR | Input Registers | Registres d'entrée | lecture seule | 1 registre de 16 bits |

Correspondance avec les codes fonction et les méthodes du client `pymodbus` :

| Sigle | Code fonction | Méthode de lecture | Méthode d'écriture |
|-------|--------------|--------------------|--------------------|
| CO | 1 (Read Coils) | `read_coils()` | `write_coil()`, `write_coils()` |
| DI | 2 (Read Discrete Inputs) | `read_discrete_inputs()` | - |
| HR | 3 (Read Holding Registers) | `read_holding_registers()` | `write_register()`, `write_registers()` |
| IR | 4 (Read Input Registers) | `read_input_registers()` | - |

Dans la suite du document, les cartes mémoire sont écrites avec ces sigles : `CO 0` désigne le coil d'adresse 0, `IR 0` le registre d'entrée d'adresse 0.

## Prérequis

| Outil | Rôle | Documentation |
|-------|------|---------------|
| Git | Récupérer le dépôt et versionner le code | [git-scm.com/downloads](https://git-scm.com/downloads) |
| uv | Gérer Python, l'environnement virtuel et les dépendances | [docs.astral.sh/uv](https://docs.astral.sh/uv/) — installation : [guide officiel](https://docs.astral.sh/uv/getting-started/installation/) |
| pymodbus 3.15 | Bibliothèque Modbus (installée automatiquement par `uv`) | [pymodbus.readthedocs.io](https://pymodbus.readthedocs.io/en/latest/) |

Remarques :

- Python n'a pas besoin d'être installé séparément : `uv` télécharge la version déclarée dans `pyproject.toml` (CPython 3.13).
- Les exemples utilisent le port **502**, qui est réservé aux administrateurs sous Linux et macOS. Sur Windows, aucun privilège particulier n'est requis. Pour éviter cette contrainte, il est possible de remplacer `502` par `5020` dans les fichiers `.py` : le port est défini à un seul endroit par serveur (`ADDRESS`).

## Installation du projet

### 1. Récupérer le dépôt

```bash
git clone https://github.com/kryll13/demomodbus.git
cd demomodbus
```

### 2. Créer l'environnement virtuel et installer les dépendances

```bash
uv sync
```

Cette commande crée le dossier `.venv/`, installe CPython 3.13 si nécessaire et installe les dépendances déclarées dans `pyproject.toml`.

### 3. Vérifier l'installation

```bash
uv run python -c "import pymodbus; print(pymodbus.__version__)"
```

Résultat attendu : `3.15.0` (ou une version 3.15.x).

Aucune activation d'environnement n'est nécessaire : `uv run` utilise automatiquement le dossier `.venv/`. Pour travailler directement dans un terminal activé :

```bash
# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

## Contenu du dépôt

```
demomodbus/
├── server.py              # Serveur minimal : 100 CO, 100 DI, 100 HR, 100 IR
├── client.py              # Client minimal : lecture de HR 0, écriture de CO 0
├── new_server.py          # Serveur avec simulation de température (asynchrone)
├── new_client_on.py       # Client qui allume le chauffage (CO 0)
├── new_client_off.py      # Client qui éteint le chauffage (CO 0)
├── temp_server.py         # Variante : température dans les HR
├── simu.py                # Simulation thermique sans Modbus
├── pyproject.toml         # Déclaration du projet et des dépendances
├── uv.lock                # Versions exactes des dépendances
├── README.md              # Ce document
└── LICENSE                # Licence du projet
```

`pyproject.toml` fixe les versions utilisées pendant le travail :

```toml
[project]
name = "demomodbus"
version = "0.1.0"
description = "ModBus TCP server and client with Python and pymodbus package"
readme = "README.md"
requires-python = ">=3.13,<3.14"
dependencies = [
    "pymodbus>=3.15,<3.16",
]
```

## Étape 1 : le serveur minimal

Objectif : démarrer un serveur Modbus TCP qui expose quatre blocs de 100 données.

Code de `server.py` :

```python
from pymodbus.server import StartTcpServer
from pymodbus.simulator import DataType, SimData, SimDevice

store = SimDevice(
    id=1,
    simdata=(
        [SimData(0, count=100, values=False, datatype=DataType.BITS)],
        [SimData(0, count=100, values=False, datatype=DataType.BITS)],
        [SimData(0, count=100, values=13, datatype=DataType.REGISTERS)],
        [SimData(0, count=100, values=0, datatype=DataType.REGISTERS)],
    ),
)

StartTcpServer(context=store, address=("0.0.0.0", 502))
```

Commande :

```bash
uv run server.py
```

Résultat attendu : le processus reste actif et n'affiche rien. C'est le comportement normal : `pymodbus` n'active aucun journal par défaut. Le serveur est prêt lorsqu'un client répond (étape 2). Pour afficher les journaux de `pymodbus`, ajouter ces deux lignes en tête de `server.py` :

```python
from pymodbus import pymodbus_apply_logging_config

pymodbus_apply_logging_config("INFO")  # DEBUG pour le détail des requêtes
```

Le démarrage est alors signalé sur la sortie d'erreur :

```text
2026-01-01 10:00:00,000 INFO  base:92 Server listening.
```

### Comprendre le modèle de données

Depuis pymodbus 3.15, les anciens blocs de données (`ModbusDeviceContext`, `ModbusSequentialDataBlock`) sont dépréciés et seront supprimés en version 4.0. Le modèle de données se décrit désormais avec deux objets :

- `SimData` : un groupe de données contiguës de même type. `SimData(0, count=100, values=13, datatype=DataType.REGISTERS)` définit 100 registres, d'adresse 0 à 99, contenant la valeur 13.
- `SimDevice` : l'appareil. `id=1` correspond à l'identifiant d'esclave (unit id) utilisé par les requêtes Modbus.

Le paramètre `simdata` reçoit les quatre blocs **dans un ordre imposé** : CO (Coils), DI (Discrete Inputs), HR (Holding Registers), IR (Input Registers). `DataType.BITS` décrit un bit (une adresse correspond à un seul booléen), `DataType.REGISTERS` décrit un registre de 16 bits.

L'adresse `0.0.0.0` fait écouter le serveur sur toutes les interfaces réseau ; les clients se connectent à l'adresse locale `127.0.0.1`.

Seules les données déclarées sont accessibles : toute adresse non déclarée reçoit une exception `ILLEGAL_ADDRESS` du serveur.

## Étape 2 : le client minimal

Objectif : lire une donnée et écrire une donnée depuis un programme client.

Code de `client.py` :

```python
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('127.0.0.1', port=502)
client.connect()

result = client.read_holding_registers(address=0)
if not result.isError():
    print("Valeur de HR 0 :", result.registers)

client.write_coil(address=0, value=True)

client.close()
```

Commande, dans un second terminal, serveur démarré :

```bash
uv run client.py
```

Résultat attendu :

```text
Valeur de HR 0 : [13]
```

Points à vérifier :

- `client.connect()` établit la connexion TCP ; `client.close()` la ferme. Le bloc `with ModbusTcpClient(...) as client:` fait les deux automatiquement.
- toute réponse peut être une erreur : `result.isError()` doit toujours être testé avant de lire `result.registers`.
- les adresses et les quantités sont des arguments nommés : `read_holding_registers(address=0, count=2)` pour lire deux registres à partir de l'adresse 0.
- les identifiants d'esclave sont égaux à 1 par défaut des deux côtés (`device_id=1` côté client, `SimDevice(id=1)` côté serveur).

## Étape 3 : le serveur simulé

Objectif : faire varier une température en temps réel et publier les valeurs dans la mémoire du serveur.

Carte mémoire de `new_server.py` :

| Adresse | Bloc | Valeur |
|---------|------|--------|
| CO 0 | Coils | Chauffage : `0` (arrêté), `1` (allumé) |
| DI 0 | Discrete Inputs | `1` si la température dépasse 25 °C |
| DI 1 | Discrete Inputs | `1` si la température est inférieure à 15 °C |
| HR 0 | Holding Registers | Non utilisé |
| IR 0 et IR 1 | Input Registers | Température en °C, type FLOAT32 |

Code de `new_server.py` :

```python
import asyncio
import random

from pymodbus.client import ModbusTcpClient
from pymodbus.server import ModbusTcpServer
from pymodbus.simulator import DataType, SimData, SimDevice

DEVICE_ID = 1
ADDRESS = ("0.0.0.0", 502)

READ_COILS = 1
READ_DISCRETE_INPUTS = 2
READ_INPUT_REGISTERS = 4

CO_HEATING = 0
DI_HIGH_TEMP = 0
DI_LOW_TEMP = 1
IR_TEMPERATURE = 0

TEMP_START = 20.0
TEMP_MIN = 10.0
TEMP_MAX = 30.0
TEMP_HIGH = 25.0
TEMP_LOW = 15.0


def to_registers(temperature: float) -> list[int]:
    """Convertit une température en 2 registres FLOAT32."""
    return ModbusTcpClient.convert_to_registers(
        temperature, ModbusTcpClient.DATATYPE.FLOAT32
    )


def build_device() -> SimDevice:
    """Décrit les 4 blocs de données du serveur."""
    return SimDevice(
        id=DEVICE_ID,
        simdata=(
            [SimData(CO_HEATING, values=False, datatype=DataType.BITS)],
            [
                SimData(DI_HIGH_TEMP, values=False, datatype=DataType.BITS),
                SimData(DI_LOW_TEMP, values=False, datatype=DataType.BITS),
            ],
            [SimData(0, values=0, datatype=DataType.REGISTERS)],
            [SimData(IR_TEMPERATURE, values=TEMP_START, datatype=DataType.FLOAT32)],
        ),
    )


async def temperature_simulation(server: ModbusTcpServer) -> None:
    """Fait varier la température selon l'état du chauffage."""
    temperature = TEMP_START

    while True:
        heating_on = (
            await server.async_getValues(DEVICE_ID, READ_COILS, CO_HEATING, count=1)
        )[0]

        temperature += (
            random.uniform(0.1, 0.5) if heating_on else -random.uniform(0.1, 0.3)
        )
        temperature = min(max(temperature, TEMP_MIN), TEMP_MAX)

        await server.async_setValues(
            DEVICE_ID, READ_INPUT_REGISTERS, IR_TEMPERATURE, to_registers(temperature)
        )
        await server.async_setValues(
            DEVICE_ID, READ_DISCRETE_INPUTS, DI_HIGH_TEMP, [temperature > TEMP_HIGH]
        )
        await server.async_setValues(
            DEVICE_ID, READ_DISCRETE_INPUTS, DI_LOW_TEMP, [temperature < TEMP_LOW]
        )

        print(f"T = {temperature:.1f} °C | Chauffage = {'ON' if heating_on else 'OFF'}")
        await asyncio.sleep(1)


async def main() -> None:
    server = ModbusTcpServer(build_device(), address=ADDRESS)
    await server.serve_forever(background=True)

    print("Serveur Modbus TCP démarré sur le port 502...")
    await temperature_simulation(server)


if __name__ == "__main__":
    asyncio.run(main())
```

### Lancer et observer

```bash
# Terminal 1 : le serveur
uv run new_server.py

# Terminal 2 : allumer le chauffage
uv run new_client_on.py

# Terminal 2 : éteindre le chauffage
uv run new_client_off.py
```

Résultat attendu dans le terminal du serveur : une ligne par seconde. Les premières lignes indiquent `OFF` ; après l'exécution de `new_client_on.py`, la ligne suivante indique `ON` et la température augmente à chaque seconde. Le serveur s'arrête avec `Ctrl+C`.

```text
Serveur Modbus TCP démarré sur le port 502...
T = 20.3 °C | Chauffage = OFF
T = 20.1 °C | Chauffage = OFF
T = 20.4 °C | Chauffage = ON
T = 20.9 °C | Chauffage = ON
```

Vérifications à réaliser :

- la température augmente lorsque `new_client_on.py` a été exécuté, elle diminue après `new_client_off.py` ;
- la température reste comprise entre 10 °C et 30 °C, bornes appliquées par `TEMP_MIN` et `TEMP_MAX` ;
- au-delà de 25 °C, DI 0 passe à 1 ; en dessous de 15 °C, DI 1 passe à 1 ;
- CO 0 reflète la dernière commande reçue : `True` après `new_client_on.py`, `False` après `new_client_off.py`.

### Points techniques

**Écrire dans la mémoire du serveur.** Depuis la version 3.15, le serveur construit sa mémoire à partir des `SimDevice` fournis à la construction. Pour faire évoluer ces données en cours d'exécution, il écrit directement dedans avec deux méthodes :

- `await server.async_getValues(device_id, code_fonction, adresse, count)` : lecture ;
- `await server.async_setValues(device_id, code_fonction, adresse, valeurs)` : écriture.

Le deuxième argument est le code fonction Modbus employé par le client. Il détermine le bloc mémoire concerné :

| Code | Fonction Modbus | Bloc |
|------|-----------------|------|
| 1 | Read Coils | CO |
| 2 | Read Discrete Inputs | DI |
| 3 | Read Holding Registers | HR |
| 4 | Read Input Registers | IR |

**Tâche de simulation.** Le serveur est asynchrone : `serve_forever(background=True)` le démarre sans bloquer la boucle d'événements, et la boucle `while True` de la simulation s'exécute dans la même boucle avec `asyncio.sleep(1)`. Le serveur reste donc joignable pendant que la simulation s'exécute.

**Type FLOAT32.** La température occupe deux registres de 16 bits. Le serveur encode la valeur avec `convert_to_registers()`, le client la décode avec `convert_from_registers()` ; il faut donc lire deux registres (`count=2`).

## Étape 4 : lire la température depuis un client

Objectif : décoder une valeur flottante stockée sur deux registres.

```python
from pymodbus.client import ModbusTcpClient

with ModbusTcpClient("127.0.0.1", port=502) as client:
    response = client.read_input_registers(0, count=2)
    temperature = ModbusTcpClient.convert_from_registers(
        response.registers, ModbusTcpClient.DATATYPE.FLOAT32
    )
    print(f"{temperature:.1f} °C")
```

Résultat attendu : une température comprise entre 10 et 30 °C, proche de la valeur affichée par le serveur.

La lecture de l'état des capteurs se fait de la même manière :

```python
with ModbusTcpClient("127.0.0.1", port=502) as client:
    print("Chauffage :", client.read_coils(0, count=1).bits[0])
    print("Seuils    :", client.read_discrete_inputs(0, count=2).bits[:2])
```

## Exercices

Chaque exercice est indépendant et vérifiable avec les commandes des étapes précédentes.

1. Changer de port. Remplacer `502` par `5020` dans `server.py`, `client.py`, `new_server.py`, `new_client_on.py`, `new_client_off.py` et `temp_server.py`. Vérification : `uv run server.py` puis `uv run client.py` affiche toujours `[13]` et le serveur démarre sans privilèges administrateur.
2. Modifier un seuil. Dans `new_server.py`, passer `TEMP_HIGH` de 25 à 22. Vérification : DI 0 passe à 1 alors que la température affichée est comprise entre 22 et 30 °C.
3. Changer de type de donnée. Remplacer `DataType.FLOAT32` par `DataType.REGISTERS` dans `new_server.py`, et publier la température multipliée par 10 (par exemple `int(temperature * 10)`) à la place de `to_registers(temperature)`. Vérification : la lecture se fait avec `read_input_registers(0, count=1)` et la valeur obtenue est comprise entre 100 et 300.
4. Observer les échanges. Ajouter `pymodbus_apply_logging_config("DEBUG")` en tête de `new_server.py`. Vérification : le terminal du serveur affiche la trame reçue (`recv:`), la requête décodée, puis la trame renvoyée (`send:`) :

```text
DEBUG transport:307 recv: 0x0 0x1 0x0 0x0 0x0 0x6 0x1 0x4 0x0 0x0 0x0 0x2 extra data:
DEBUG decoders:86 decoded PDU function_code(4 sub -1) -> ReadInputRegistersRequest(...)
DEBUG transport:356 send: 0x0 0x1 0x0 0x0 0x0 0x5 0x1 0x4 0x2 0x0 0xc3
```

## Variantes fournies

### `temp_server.py`

Même principe que `new_server.py`, avec une carte mémoire réduite :

| Adresse | Bloc | Valeur |
|---------|------|--------|
| CO 0 | Coils | Chauffage, actif au démarrage |
| DI 0 | Discrete Inputs | Non utilisé |
| HR 0 et HR 1 | Holding Registers | Température en °C, type FLOAT32 |
| IR 0 | Input Registers | Non utilisé |

La température augmente uniquement lorsque le chauffage est alimenté, et elle est plafonnée à 30 °C.

```bash
uv run temp_server.py
```

Sortie attendue, une ligne par seconde :

```text
Serveur Modbus TCP démarré sur le port 502...
T = 20.3 °C | Chauffage = ON
T = 20.6 °C | Chauffage = ON
```

Lecture de HR 0 et HR 1 :

```python
with ModbusTcpClient("127.0.0.1", port=502) as client:
    response = client.read_holding_registers(0, count=2)
    temperature = ModbusTcpClient.convert_from_registers(
        response.registers, ModbusTcpClient.DATATYPE.FLOAT32
    )
    print(f"{temperature:.1f} °C")
```

Pour arrêter la montée de la température : `uv run new_client_off.py` (CO 0 passe à 0). Dans cette variante, la température n'étant jamais refroidie, elle reste constante.

### `simu.py`

Simulation thermique sans Modbus, utile pour comprendre l'effet d'un seuil de sécurité avant de l'implémenter en Modbus. Le modèle comporte une température extérieure, une capacité thermique, des pertes thermiques et une puissance de chauffage maximale ; la puissance n'est appliquée que si le seuil de sécurité de 80 °C n'est pas atteint, auquel cas le chauffage est coupé.

```bash
uv run simu.py
```

La simulation exécute 200 itérations et affiche l'état à chaque étape ; le chauffage est coupé peu avant la dernière itération :

```text
t=0s ; T=20.50°C ; Chauffage=True ; Sécurité=False
t=1s ; T=21.00°C ; Chauffage=True ; Sécurité=False
...
t=199s ; T=78.93°C ; Chauffage=False ; Sécurité=True
```

## Rappels Modbus

Les quatre blocs sont décrits dans la section [Dénomination de la mémoire Modbus](#dénomination-de-la-mémoire-modbus). Points d'attention pour les utiliser :

- pymodbus compte les adresses à partir de 0. Certains outils affichent l'adresse 0 des HR sous la forme 40001 : il s'agit de la même donnée.
- CO et DI se lisent bit par bit, HR et IR registre par registre. Dans les appareils décrits par ce projet, les quatre blocs sont séparés : une écriture de CO 0 ne modifie pas HR 0.
- une valeur sur plusieurs registres (FLOAT32 sur 2 registres, INT64 sur 4) doit être lue et écrite en une seule requête, sinon la donnée est incohérente.
- le temps de cycle minimal d'une requête Modbus TCP est de l'ordre de la milliseconde : il est inutile d'interroger plusieurs fois par seconde un appareil qui varie lentement.

## Commandes uv courantes

| Commande | Rôle | Documentation |
|----------|------|---------------|
| `uv sync` | Créer l'environnement et installer les dépendances | [sync](https://docs.astral.sh/uv/concepts/projects/sync/) |
| `uv run <script.py>` | Exécuter un script dans l'environnement du projet | [scripts](https://docs.astral.sh/uv/guides/scripts/) |
| `uv add <paquet>` | Ajouter une dépendance | [dépendances](https://docs.astral.sh/uv/concepts/projects/dependencies/) |
| `uv update` | Mettre à jour les dépendances verrouillées | [mise à jour des versions](https://docs.astral.sh/uv/concepts/projects/sync/#upgrading-locked-package-versions) |
| `uv lock` | Recalculer `uv.lock` | [création du fichier verrou](https://docs.astral.sh/uv/concepts/projects/sync/#creating-the-lockfile) |
| `uv list` | Lister les dépendances installées | [référence CLI](https://docs.astral.sh/uv/reference/cli/) |
| `uv python list` | Lister les versions de Python disponibles | [versions de Python](https://docs.astral.sh/uv/concepts/python-versions/) |

Documentation complète : [docs.astral.sh/uv](https://docs.astral.sh/uv/).

## Conserver le travail avec Git

```bash
# Vérifier l'état du dépôt
git status

# Enregistrer les modifications
git add .
git commit -m "description courte du changement"

# Consulter l'historique
git log --oneline

# Publier sur le dépôt distant
git push -u origin main
```

Ces commandes supposent que Git est configuré. Au premier commit seulement :

```bash
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"
```

Le dossier `.venv/` n'apparaît pas dans `git status` : `uv` y écrit lui-même un `.gitignore` contenant `*`. Les autres fichiers à ne pas versionner (`__pycache__/`, fichiers de configuration locaux) peuvent être ignorés avec un fichier `.gitignore` à la racine du dépôt.

Documentation : [git-scm.com/doc](https://git-scm.com/doc).

## Dépannage

| Symptôme | Cause probable | Correction |
|----------|----------------|------------|
| Aucune sortie dans le terminal du serveur | comportement normal, `pymodbus` n'active aucun journal par défaut | vérifier la disponibilité du serveur avec un client, ou activer les journaux avec `pymodbus_apply_logging_config("INFO")` |
| `Permission denied` au démarrage du serveur | le port 502 est réservé aux administrateurs sous Linux et macOS | utiliser `sudo uv run server.py` ou passer le port à 5020 |
| `ConnectionException: Failed to connect` | le serveur n'est pas démarré, ou l'adresse / le port ne correspond pas | vérifier que le serveur écoute, et que l'adresse client correspond à l'écoute (`127.0.0.1` pour `0.0.0.0`) |
| `ModbusIOException: No response received` | le client interroge une adresse inexistante, ou le type de requête ne correspond pas au bloc | contrôler l'adresse et le code fonction ; les adresses non déclarées lèvent `ILLEGAL_ADDRESS` |
| Température qui ne varie pas | CO 0 n'a jamais été mis à 1 | exécuter `uv run new_client_on.py` |
| Valeur de température incohérente | les deux registres du FLOAT32 n'ont pas été lus dans la même requête | lire `count=2` en une seule requête |
| `TypeError` sur `SimDevice` | un des quatre blocs de `simdata` est vide | chaque bloc doit contenir au moins un `SimData` |
| Environnement Python incohérent | dépendances désynchronisées | `uv sync` |
| Le client répond avec des valeurs inattendues | un second serveur écoute déjà sur le port 502 | arrêter le processus serveur lancé précédemment (`Ctrl+C`) avant d'en démarrer un autre |

## Références

### pymodbus (version utilisée : 3.15)

- Documentation : <https://pymodbus.readthedocs.io/en/latest/>
- API client : <https://pymodbus.readthedocs.io/en/latest/source/client.html>
- API serveur : <https://pymodbus.readthedocs.io/en/latest/source/server.html>
- Simulateur et modèle de données `SimData` / `SimDevice` : <https://pymodbus.readthedocs.io/en/latest/source/simulator.html>
- Exemples officiels : <https://pymodbus.readthedocs.io/en/latest/source/examples.html> et <https://github.com/pymodbus-dev/pymodbus/tree/dev/examples>
- Migration vers la version 4.0 : <https://pymodbus.readthedocs.io/en/dev/source/upgrade_40.html>
- Notes de version : <https://pymodbus.readthedocs.io/en/latest/source/changelog.html>

### Outils

- uv : <https://docs.astral.sh/uv/> — installation : <https://docs.astral.sh/uv/getting-started/installation/>
- Git : <https://git-scm.com/downloads> — documentation : <https://git-scm.com/doc>
- Cours Git (merci Quentin) : <https://buzut.net/cours/versioning-avec-git/comprendre-git-et-le-versioning>

### Modbus et Python

- Modbus Organization : <https://modbus.org/>
- Spécifications Modbus (protocole et guide d'implémentation TCP) : <https://modbus.org/specs.php>
- Documentation Python 3.13 : <https://docs.python.org/3.13/>

---

Travail dirigé sur le protocole Modbus TCP avec Python 3.13, pymodbus 3.15, uv et Git.
