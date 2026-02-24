# Module d'Audit d'Obsolescence Réseau

## Table des matières

1. [Description](#description)
2. [Architecture du projet](#architecture-du-projet)
3. [Fonctionnalités](#fonctionnalités)
   - [Scan du réseau](#1-scan-du-réseau)
   - [Vérification d'obsolescence](#2-vérification-dobsolescence)
   - [Rapports multiformats](#3-rapports-multiformats)
   - [Interface utilisateur](#4-interface-utilisateur)
4. [Prérequis](#prérequis)
   - [Logiciels](#logiciels)
   - [Bibliothèques Python](#bibliothèques-python)
5. [Installation](#installation)
   - [Windows](#windows)
   - [Linux](#linux)
6. [Utilisation](#utilisation)
   - [Lancement du script](#lancement-du-script)
   - [Scanner un réseau](#scanner-un-réseau)
   - [Importer un CSV existant](#importer-un-csv-existant)
   - [Afficher les résultats](#afficher-les-résultats)
   - [Lister les versions d'un OS](#lister-les-versions-dun-os)
   - [Générer des rapports](#générer-des-rapports)
7. [Exemples de rapports](#exemples-de-rapports)
   - [Format CSV](#format-csv)
   - [Format JSON](#format-json)
   - [Format HTML](#format-html)
8. [Limitations](#limitations)
9. [Emplacement des fichiers générés](#emplacement-des-fichiers-générés)

---

## Description

Le **Module d'Audit d'Obsolescence Réseau** est un outil Python conçu pour automatiser l'inventaire des équipements réseau et identifier les systèmes d'exploitation obsolètes ou approchant leur fin de support (EOL - End of Life).

Ce module permet aux administrateurs systèmes et réseaux de :
- Détecter automatiquement les OS présents sur un réseau via Nmap
- Interroger l'API **endoflife.date** pour obtenir les dates de fin de support
- Qualifier le statut EOL de chaque système (supporté, EOL imminent, non supporté)
- Générer des rapports exploitables aux formats CSV, JSON et HTML

L'objectif principal est de fournir un inventaire réseau minimal et de qualifier le statut de support/EOL des éléments détectés, conformément aux exigences de sécurité et de conformité.

---

## Architecture du projet

Le module est structuré autour des composants suivants :

```
audit_os.py
├── Gestion SSL
│   └── Contournement des erreurs de certificats SSL (Windows)
│
├── Scan réseau
│   ├── scan_network()      : Exécute Nmap avec détection OS
│   └── parse_xml()         : Parse le fichier XML généré par Nmap
│
├── Extraction d'informations
│   ├── extract_os()        : Identifie l'OS et sa version
│   └── extract_common_name() : Récupère le nom via certificat SSL
│
├── Vérification EOL
│   ├── get_eol_from_api()  : Interroge endoflife.date
│   └── get_status()        : Détermine le statut EOL
│
├── Import/Export
│   ├── import_csv()        : Importe un inventaire CSV existant
│   └── generate_report()   : Génère les rapports CSV, JSON, HTML
│
├── Affichage
│   ├── show_hosts()        : Affiche les résultats dans la console
│   └── list_all_versions() : Liste toutes les versions d'un OS
│
└── Interface
    └── menu()              : Menu interactif en ligne de commande
```

---

## Fonctionnalités

### 1. Scan du réseau

Le module utilise **Nmap** pour scanner une plage réseau et identifier les hôtes actifs avec leurs systèmes d'exploitation.

**Capacités de détection :**
- Adresse IP de chaque hôte
- Hostname réseau (via DNS inverse)
- CommonName (via certificat SSL si disponible)
- Système d'exploitation (OS detection)
- Version de l'OS

**Systèmes supportés :**
- Windows (7, 8, 8.1, 10, 11, Vista, XP)
- Windows Server (2003, 2008, 2012, 2016, 2019, 2022)
- Ubuntu (toutes versions)
- Debian (toutes versions)
- Linux générique

**Commande Nmap utilisée :**
```bash
nmap --privileged -O -sV -Pn --osscan-guess --script ssl-cert -T4 -oX scan.xml <réseau>
```

### 2. Vérification d'obsolescence

Le module interroge l'API **endoflife.date** pour récupérer les dates de fin de support (EOL) de chaque système détecté.

**Statuts EOL possibles :**
- **SUPPORTÉ** : Le système est encore supporté (EOL > 1 an)
- **EOL < 1 AN** : Le support se termine dans moins d'un an
- **EOL IMMINENT** : Le support se termine dans moins de 90 jours
- **NON SUPPORTÉ** : Le système n'est plus supporté (date EOL dépassée)
- **Version inconnue** : La version n'a pas pu être identifiée par l'API
- **Version non détectable** : Nmap n'a pas réussi à identifier la version

**Mise en cache :**
Les résultats de l'API sont mis en cache pour éviter les requêtes multiples et améliorer les performances.

### 3. Rapports multiformats

Le module génère automatiquement trois types de rapports :

#### CSV (Comma-Separated Values)
Format tabulaire compatible avec Excel, LibreOffice, et la plupart des outils d'analyse de données.

#### JSON (JavaScript Object Notation)
Format structuré idéal pour l'intégration avec d'autres outils, scripts Python, ou systèmes de gestion.

#### HTML (HyperText Markup Language)
Rapport visuel avec tableau interactif, mise en forme colorée par statut, et présentation professionnelle pour partage avec la direction ou documentation.

### 4. Interface utilisateur

Le module propose un **menu interactif** en ligne de commande avec les options suivantes :

1. **Scanner réseau** : Lance un scan Nmap sur une plage IP
2. **Importer CSV** : Charge un inventaire existant depuis un fichier CSV
3. **Afficher hôtes** : Affiche les résultats dans la console
4. **Lister versions d'un OS** : Interroge l'API pour voir toutes les versions disponibles
5. **Générer rapport** : Crée les fichiers CSV, JSON et HTML
0. **Quitter** : Ferme le programme

---

## Prérequis

### Logiciels

- **Python 3.6 ou supérieur**
- **Nmap** installé et accessible dans le PATH
- **Droits administrateur/root** pour le scan OS avec Nmap :
  - **Windows** : Exécuter le script en tant qu'administrateur
  - **Linux** : Utiliser `sudo` ou configurer les capacités Nmap (voir Installation)
- **Connexion internet** pour interroger l'API endoflife.date

### Bibliothèques Python

Toutes les bibliothèques utilisées sont **natives** à Python. Aucune installation via `pip` n'est requise.

```python
import subprocess
import re
import csv
import os
import json
from datetime import datetime
import xml.etree.ElementTree as ET
import platform
from pathlib import Path
import urllib.request
import urllib.error
import ssl
```

---

## Installation

### Windows

1. **Télécharger le script** `audit_os.py` sur votre machine

2. **Vérifier l'installation de Python** :
   ```cmd
   python --version
   ```
   (Doit afficher Python 3.6 ou supérieur)

3. **Vérifier l'installation de Nmap** :
   ```cmd
   nmap --version
   ```
   Si Nmap n'est pas installé, téléchargez-le depuis [nmap.org](https://nmap.org/download.html)

4. **Lancer le script en tant qu'administrateur** :
   - Clic droit sur l'invite de commandes → "Exécuter en tant qu'administrateur"
   ```cmd
   python audit_os.py
   ```

### Linux

1. **Télécharger le script** `audit_os.py` sur votre machine

2. **Vérifier l'installation de Python** :
   ```bash
   python3 --version
   ```

3. **Vérifier l'installation de Nmap** :
   ```bash
   nmap --version
   ```
   Si Nmap n'est pas installé :
   ```bash
   sudo apt install nmap  # Debian/Ubuntu
   sudo yum install nmap  # RedHat/CentOS
   ```

4. **Configurer les capacités Nmap** (pour exécution sans root) :
   ```bash
   sudo setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip $(which nmap)
   ```

5. **Rendre le script exécutable** :
   ```bash
   chmod +x audit_os.py
   ```

6. **Lancer le script** :
   ```bash
   python3 audit_os.py
   ```
   ou
   ```bash
   ./audit_os.py
   ```

---

## Utilisation

### Lancement du script

**Windows (en administrateur) :**
```cmd
python audit_os.py
```

**Linux :**
```bash
python3 audit_os.py
```

### Scanner un réseau

1. Choisir l'option **1** dans le menu
2. Entrer la plage réseau à scanner (exemples) :
   - `192.168.1.0/24` (254 hôtes)
   - `10.5.70.0/24`
   - `172.16.0.0/16`

Le script effectue alors :
- Scan Nmap avec détection OS
- Analyse du fichier XML généré
- Interrogation de l'API endoflife.date
- Affichage des résultats dans la console

**Exemple de sortie :**
```
====================================================================================
IP               Hostname / CN                  OS                   Version                        EOL            Statut
====================================================================================
192.168.1.10     SRV-DC01                       Windows Server       2012 R2                        2023-10-10     NON SUPPORTÉ
192.168.1.20     SRV-WEB                        Ubuntu               20.04                          2025-04-02     SUPPORTÉ
192.168.1.30     DESKTOP-ABC123                 Windows              10                             2025-10-14     EOL < 1 AN
====================================================================================
```

### Importer un CSV existant

1. Choisir l'option **2** dans le menu
2. Fournir le nom du fichier CSV (exemple : `inventaire.csv`)

**Format CSV attendu :**
```csv
IP,Hostname,OS_Name,OS_Version
192.168.1.10,SRV-DC01,Windows Server,2012 R2
192.168.1.20,SRV-WEB,Ubuntu,20.04
192.168.1.30,DESKTOP-ABC123,Windows,10
```

Le script recherche automatiquement le fichier dans plusieurs emplacements :
- Répertoire courant
- Dossier de sortie configuré
- Chemin absolu fourni

### Afficher les résultats

Choisir l'option **3** dans le menu pour afficher un tableau formaté des hôtes en mémoire.

### Lister les versions d'un OS

1. Choisir l'option **4** dans le menu
2. Entrer le nom de l'OS (choix possibles) :
   - `Windows`
   - `Windows Server`
   - `Ubuntu`
   - `Debian`

**Exemple de sortie :**
```
================================================================================
WINDOWS - Versions et dates EOL
================================================================================
Version              Support         EOL             Statut
--------------------------------------------------------------------------------
11                   2026-10-13      2028-10-10      Actif
10                   2025-05-09      2025-10-14      324 jours restants
8.1                  2018-01-09      2023-01-10      Terminé
7                    2015-01-13      2020-01-14      Terminé
================================================================================
```

### Générer des rapports

1. Choisir l'option **5** dans le menu
2. (Optionnel) Fournir un nom de base pour les rapports, exemple : `audit_janvier_2026`

Les fichiers sont automatiquement générés dans le dossier de sortie :
- `audit_janvier_2026.csv`
- `audit_janvier_2026.json`
- `audit_janvier_2026.html`

Si aucun nom n'est fourni, le nom par défaut `rapport` est utilisé.

---

## Exemples de rapports

### Format CSV

Le rapport CSV contient les colonnes suivantes :

| IP            | Hostname/CN    | OS             | Version  | EOL        | Statut        |
|---------------|----------------|----------------|----------|------------|---------------|
| 192.168.1.10  | SRV-DC01       | Windows Server | 2012 R2  | 2023-10-10 | NON SUPPORTÉ  |
| 192.168.1.20  | SRV-WEB        | Ubuntu         | 20.04    | 2025-04-02 | SUPPORTÉ      |
| 192.168.1.30  | DESKTOP-ABC123 | Windows        | 10       | 2025-10-14 | EOL < 1 AN    |

**Utilisation :** Compatible avec Excel, LibreOffice Calc, outils d'analyse de données.

### Format JSON

Le rapport JSON structure les données de manière hiérarchique :

```json
[
    {
        "ip": "192.168.1.10",
        "hostname": "SRV-DC01",
        "os": "Windows Server",
        "version": "2012 R2",
        "eol": "2023-10-10",
        "status": "NON SUPPORTÉ"
    },
    {
        "ip": "192.168.1.20",
        "hostname": "SRV-WEB",
        "os": "Ubuntu",
        "version": "20.04",
        "eol": "2025-04-02",
        "status": "SUPPORTÉ"
    },
    {
        "ip": "192.168.1.30",
        "hostname": "DESKTOP-ABC123",
        "os": "Windows",
        "version": "10",
        "eol": "2025-10-14",
        "status": "EOL < 1 AN"
    }
]
```

**Utilisation :** Intégration avec scripts Python, APIs REST, systèmes de monitoring.

### Format HTML

Le rapport HTML inclut :

- **En-tête professionnel** avec titre et date de génération
- **Tableau interactif** avec les colonnes :
  - IP
  - Hostname/CN
  - OS
  - Version
  - Date EOL
  - Statut (avec badges colorés)
- **Badges de statut colorés** :
  - 🔴 Rouge : NON SUPPORTÉ
  - 🟠 Orange : EOL IMMINENT / EOL < 1 AN
  - 🟢 Vert : SUPPORTÉ
  - ⚪ Gris : Version inconnue / non détectable
- **Mise en forme responsive** pour consultation sur différents appareils
- **Style professionnel** avec survol de lignes pour faciliter la lecture

**Utilisation :** Présentation aux équipes, documentation, rapports de conformité.

---

## Limitations

### 1. Détection Linux limitée avec Nmap

**Problème :** Nmap a des difficultés à détecter précisément les versions de distributions Linux, en particulier pour Ubuntu et Debian.

**Impact :** Les hôtes Linux peuvent apparaître avec le statut :
- `Version non détectée par Nmap`
- `Vérification manuelle requise (cat /etc/os-release)`

**Solution de contournement :**
- Se connecter manuellement aux machines Linux
- Exécuter : `cat /etc/os-release` ou `lsb_release -a`
- Mettre à jour l'inventaire CSV avec les versions correctes
- Réimporter le CSV dans le module

### 2. Privilèges requis pour le scan Nmap

**Windows :**
- Le script **DOIT** être exécuté en tant qu'administrateur
- Sans droits admin, la détection OS échouera

**Linux :**
- Option 1 : Exécuter avec `sudo python3 audit_os.py`
- Option 2 : Configurer les capacités Nmap (recommandé) :
  ```bash
  sudo setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip $(which nmap)
  ```
  Cette commande permet à un utilisateur standard d'exécuter le script sans `sudo`.

### 3. Dépendance à l'API endoflife.date

**Problème :** Le module nécessite une connexion internet active pour interroger l'API.

**Impact en cas d'indisponibilité :**
- Pas de vérification EOL possible
- Les statuts afficheront "Version inconnue"

**Solution de contournement :**
- Utiliser un cache local des résultats API (déjà implémenté dans le script)
- Consulter manuellement le site [endoflife.date](https://endoflife.date/)

### 4. Performance du scan Nmap

**Durée du scan :**
- `/24` (254 hôtes) : 5-15 minutes selon le réseau
- `/16` (65 534 hôtes) : Plusieurs heures

**Recommandations :**
- Limiter les scans aux sous-réseaux pertinents
- Utiliser l'option d'import CSV pour les grands réseaux
- Planifier les scans pendant les heures creuses
- Augmenter le niveau de timing Nmap si besoin (`-T5` au lieu de `-T4`)

**Timeout configuré :** Le script a un timeout de 1800 secondes (30 minutes) par scan.

---

## Emplacement des fichiers générés

Les rapports et fichiers générés sont automatiquement enregistrés dans :

**Windows :**
```
C:\Users\<VotreNom>\Documents\audit_rapports\
```

**Linux :**
```
~/audit_rapports/
```

**Fichiers créés :**
- `scan.xml` : Résultat brut du scan Nmap
- `rapport.csv` (ou nom personnalisé)
- `rapport.json` (ou nom personnalisé)
- `rapport.html` (ou nom personnalisé)

Le chemin exact est affiché au lancement du script :
```
Dossier de sortie: /home/user/audit_rapports
```

---

## Support et Contact

Pour toute question ou problème concernant ce module, veuillez contacter votre formateur ou référent technique.

## Licence

Module développé dans le cadre d'une épreuve de formation en administration systèmes et réseaux.

---

**Version :** 1.0  
**Date de création :** Février 2026  
**Auteur :** [Votre Nom]
