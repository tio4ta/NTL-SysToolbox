# 🔍 Module d'Audit d'Obsolescence Réseau

<div align="center">

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Nmap](https://img.shields.io/badge/Nmap-Required-green.svg)
![Windows SSL Fix](https://img.shields.io/badge/Windows-SSL%20Fix%20Requis-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Production-success.svg)

*Un outil puissant pour auditer l'obsolescence des systèmes d'exploitation de votre parc réseau*

[Fonctionnalités](#-fonctionnalités) • [🚨 Windows SSL](#-fix-ssl-windows-obligatoire) • [Installation](#-installation) • [Utilisation](#-utilisation)

</div>

---

## 📋 Table des matières

- [Vue d'ensemble](#-vue-densemble)
- [Fonctionnalités](#-fonctionnalités)
- [SSL Windows](#ssl-windows-obligatoire)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Architecture](#-architecture)
- [Limitations](#-limitations)
- [Exemples de rapports](#-exemples-de-rapports)
- [Dépannage](#-dépannage)
- [Roadmap](#-roadmap)
- [Contribution](#-contribution)
- [Licence](#-licence)

---

## 🎯 Vue d'ensemble

Ce script Python réalise un **audit complet d'obsolescence** des systèmes d'exploitation détectés sur un réseau, en combinant :

- 🔎 **Scan réseau** avec Nmap pour la découverte et l'identification des OS
- 📅 **Vérification EOL** via l'API [endoflife.date](https://endoflife.date)
- 📊 **Génération de rapports** multiformats (CSV, JSON, HTML)

### Pourquoi ce projet ?

Dans un environnement IT, maintenir à jour l'inventaire des systèmes et connaître leur statut de support est **crucial pour la sécurité** et la conformité. Ce module automatise cette tâche fastidieuse et fournit des rapports exploitables pour les équipes infrastructure et sécurité.

---

## ✨ Fonctionnalités

### 🔍 Découverte réseau avancée

- Scan automatisé d'une plage IP avec **Nmap**
- Détection OS avec empreintes avancées (`-O`, `-sV`, `--osscan-guess`)
- Extraction du **Common Name** des certificats SSL
- Support des OS : Windows Desktop, Windows Server, Ubuntu, Debian, Linux générique

### 📅 Vérification d'obsolescence

- Interrogation de l'API **endoflife.date** pour les dates EOL
- Cache intelligent pour optimiser les appels API
- Calcul automatique du statut :
  - ✅ **SUPPORTÉ**
  - ⚠️ **EOL < 1 AN**
  - 🔴 **EOL IMMINENT**
  - ❌ **NON SUPPORTÉ**

### 📊 Rapports multiformats

| Format | Usage |
|--------|-------|
| **CSV** | Import Excel / Power BI / bases de données |
| **JSON** | Intégration avec outils d'automatisation |
| **HTML** | Consultation visuelle avec code couleur |

### 🎮 Interface utilisateur

Menu interactif en ligne de commande :

```
═══════════════════════════════════════════════
   AUDIT D'OBSOLESCENCE RÉSEAU
═══════════════════════════════════════════════
1. Scanner réseau
2. Importer un CSV
3. Afficher les hôtes
4. Lister les versions d'un OS
5. Générer un rapport
6. Quitter
═══════════════════════════════════════════════
```

---

## **SSL WINDOWS (OBLIGATOIRE)**

### ⚠️ **Problème courant sur Windows**

Si vous obtenez cette erreur lors de l'utilisation du script sur Windows :

```
[!] Erreur: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1081)>
```

### 🔍 **Pourquoi cette erreur ?**

**Cause technique** : Python sur Windows utilise `urllib.request` qui s'appuie sur le magasin de certificats du système pour valider les connexions HTTPS. L'API `endoflife.date` utilise des certificats **Let's Encrypt** qui ne sont pas toujours reconnus correctement par Python sur certains serveurs Windows, notamment :

- Serveurs Windows anciens (2012 R2, 2016)
- Installations Python personnalisées
- Environnements avec proxy d'entreprise
- Magasins de certificats Windows incomplets ou corrompus

**En résumé** : Python Windows ne trouve pas le certificat racine nécessaire pour valider `https://endoflife.date`, même si le certificat est parfaitement valide.

### 📝 **Explication du fix**

| Ligne | Effet |
|-------|-------|
| `import ssl` | Importe le module SSL standard Python |
| `ssl._create_default_https_context = ssl._create_unverified_context` | **Monkey patch** : remplace le contexte SSL par défaut pour ignorer la vérification des certificats |

**Est-ce sécurisé ?** ✅ **OUI** dans ce cas :
- `endoflife.date` utilise HTTPS Let's Encrypt valide
- Le problème vient de Python Windows, pas du site
- Aucune donnée sensible n'est transmise (API publique en lecture seule)
- Alternative : installer `certifi` via `pip`, mais le fix est plus simple

### 🧪 **Test rapide du fix**

Après avoir ajouté les 3 lignes, testez en console Python :

```python
python -c "import ssl; ssl._create_default_https_context = ssl._create_unverified_context; import urllib.request, json; print(json.load(urllib.request.urlopen('https://endoflife.date/api/windows.json'))[:2])"
```

**Résultat attendu** : Liste des 2 premières versions Windows

```json
[{'cycle': '11', 'releaseDate': '2021-10-05', ...}, {'cycle': '10', ...}]
```

### 🐧 **Note pour Linux/macOS**

Ce fix **n'est PAS nécessaire** sur Linux/macOS car Python utilise correctement les certificats système. Vous pouvez l'ajouter sans impact négatif (il sera simplement ignoré si non nécessaire).

---

## 🔧 Prérequis

### Système

- **Python** 3.6 ou supérieur
- **Nmap** installé et accessible dans le PATH
- **Droits root/administrateur** pour le scan OS avec Nmap
- **Connexion internet** pour l'API endoflife.date
- **Windows** : Fix SSL (3 lignes - voir section ci-dessus)

### Bibliothèques Python

Toutes les bibliothèques utilisées sont **natives** Python (aucun `pip install` requis) :

```python
import subprocess
import xml.etree.ElementTree as ET
import json
import csv
from datetime import datetime, timedelta
from urllib.request import urlopen
import os
import re
import ssl  # Pour le fix Windows
```

---

## 📦 Installation

### 1. Cloner ou télécharger le script

```bash
git clone https://github.com/votre-repo/audit-obsolescence-reseau.git
cd audit-obsolescence-reseau
```

### 2. Installer Nmap

**Debian/Ubuntu :**
```bash
sudo apt update
sudo apt install nmap
```

**CentOS/RHEL :**
```bash
sudo yum install nmap
```

**Windows :**
- Télécharger depuis [nmap.org](https://nmap.org/download.html)
- Installer avec les options par défaut
- Ajouter au PATH système (généralement automatique)

### 3. Ajouter le fix SSL (Windows uniquement)

**⚠️ ÉTAPE CRUCIALE** : Ouvrez `audit_obsolescence.py` et ajoutez les 3 lignes du fix SSL (voir section ci-dessus)

### 4. Vérifier l'installation

```bash
# Vérifier Nmap
nmap --version

# Vérifier Python
python3 --version  # ou python --version sur Windows

# Test API endoflife.date (avec fix SSL)
python -c "import ssl; ssl._create_default_https_context = ssl._create_unverified_context; import urllib.request, json; print('API OK' if json.load(urllib.request.urlopen('https://endoflife.date/api/windows.json')) else 'API KO')"
```

### 5. Permissions

Pour le scan OS avec Nmap, exécuter avec privilèges :

```bash
# Linux/macOS
sudo python3 audit_obsolescence.py

# Windows (Invite de commandes en tant qu'Administrateur)
python audit_obsolescence.py
```

---

## 🚀 Utilisation

### Démarrage rapide

```bash
# Linux/macOS
sudo python3 audit_obsolescence.py

# Windows (en Administrateur)
python audit_obsolescence.py
```

### 1️⃣ Scanner un réseau

```
Choisissez une option: 1
Entrez la plage réseau à scanner (ex: 192.168.1.0/24): 192.168.1.0/24
```

Le script va :
- Lancer Nmap avec détection OS
- Parser le fichier XML généré
- Interroger l'API endoflife.date (avec SSL fix)
- Afficher les résultats en console

### 2️⃣ Importer un CSV existant

Si vous avez déjà un inventaire :

```
Choisissez une option: 2
Nom du fichier CSV: inventaire.csv
```

Format attendu :
```csv
IP,Hostname,OS_Name,OS_Version
192.168.1.10,SRV-DC01,Windows Server,2012 R2
192.168.1.20,SRV-WEB,Ubuntu,20.04
```

### 3️⃣ Afficher les résultats

```
Choisissez une option: 3
```

Affiche un tableau formaté :

```
════════════════════════════════════════════════════════════════════════════════
IP              Hostname / CN            OS                 Version            EOL            Statut
════════════════════════════════════════════════════════════════════════════════
192.168.1.10    SRV-DC01                 Windows Server     2012 R2            2023-10-10     NON SUPPORTÉ
192.168.1.20    SRV-WEB                  Ubuntu             20.04              2025-04-01     EOL < 1 AN
════════════════════════════════════════════════════════════════════════════════
```

### 4️⃣ Lister les versions d'un OS

```
Choisissez une option: 4
OS disponibles: Windows, Windows Server, Ubuntu, Debian
Entrez le nom de l'OS: Windows Server
```

Affiche toutes les versions avec leurs dates EOL depuis l'API.

### 5️⃣ Générer des rapports

```
Choisissez une option: 5
Nom de base pour les rapports (sans extension): audit_janvier_2026
```

Génère dans le dossier configuré (par défaut `C:\Users\Administrateur\module3_audit\` sur Windows) :
- `audit_janvier_2026.csv`
- `audit_janvier_2026.json`
- `audit_janvier_2026.html`

---

## 🏗️ Architecture

### Structure du projet

```
audit-obsolescence-reseau/
├── audit_obsolescence.py    # Script principal (avec fix SSL)
├── output/                   # Dossier de sortie (auto-créé)
│   ├── scan.xml             # Résultat brut Nmap
│   ├── rapport.csv          # Rapport CSV
│   ├── rapport.json         # Rapport JSON
│   └── rapport.html         # Rapport HTML
└── README.md                # Cette documentation
```

### Flux de traitement

```
┌─────────┐
│  Début  │
└────┬────┘
     │
     ▼
┌─────────────────┐
│ Menu interactif │
└────┬────────────┘
     │
     ├──► Scan Nmap (-O -sV ssl-cert)
     │         │
     │         ▼
     │    Parsing XML
     │         │
     ├──► Import CSV
     │         │
     ▼         ▼
┌──────────────────────┐
│ Normalisation OS     │
│ (Windows/Linux/etc)  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ API endoflife.date   │ ◄── FIX SSL ICI (urllib.request)
│ (avec cache)         │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Calcul statut EOL    │
│ (SUPPORTÉ/EOL/etc)   │
└──────┬───────────────┘
       │
       ├──► Affichage console
       │
       └──► Génération rapports (CSV/JSON/HTML)
```

### Composants principaux

#### 🔹 Configuration globale

```python
OUTPUT_DIR = "C:\\Users\\Administrateur\\module3_audit"  # Windows
EOL_CACHE = {}              # Cache API en mémoire
```

#### 🔹 Fonctions clés

| Fonction | Rôle |
|----------|------|
| `scan_network(network)` | Lance Nmap et parse le XML |
| `parse_xml(xml_file)` | Extrait IP, hostname, OS, version |
| `extract_os(os_string)` | Normalise la chaîne OS Nmap |
| `extract_common_name(host_elem)` | Récupère le CN du certificat SSL |
| `get_eol_from_api(product, version)` | **Interroge endoflife.date (avec SSL fix)** |
| `get_status(os_name, version)` | Calcule le statut EOL |
| `import_csv(csv_file)` | Import d'un inventaire existant |
| `show_hosts(hosts)` | Affichage console formaté |
| `generate_report(hosts, filename)` | Génère CSV/JSON/HTML |
| `list_all_versions(os_name)` | Liste les versions d'un OS |
| `menu()` | Interface interactive |

#### 🔹 Détection OS supportée

**Windows Desktop :**
- Windows XP, Vista, 7, 8, 8.1, 10, 11

**Windows Server :**
- Windows Server 2003, 2008 (R2), 2012 (R2)
- Windows Server 2016, 2019, 2022

**Linux :**
- Ubuntu (avec version si détectée)
- Debian (avec version si détectée)
- Linux générique (version non détectable)

---

## ⚠️ Limitations

### 🐧 Détection Linux limitée

**Problème :** Nmap ne peut pas toujours détecter la version précise d'une distribution Linux via un scan réseau.

**Raison :** La détection se base sur les empreintes TCP/IP et bannières de services, pas sur l'inspection du système de fichiers (`/etc/os-release`).

**Solution :** Pour les systèmes Linux, une **vérification manuelle** est recommandée :

```bash
# Sur la machine cible
cat /etc/os-release
lsb_release -a
uname -a
```

**Workaround :** Utilisez l'import CSV (option 2) pour compléter manuellement les versions Linux après vérification.

### 🔐 Privilèges requis

Le scan OS de Nmap (`-O`) nécessite des **droits root/administrateur** :

```bash
# Linux/macOS
sudo python3 audit_obsolescence.py

# Windows (en tant qu'Administrateur)
python audit_obsolescence.py
```

### 🌐 Dépendance API

Le script nécessite une **connexion internet** pour interroger l'API endoflife.date. En cas d'indisponibilité :

- Les dates EOL ne seront pas récupérées
- Le statut sera marqué comme "Version inconnue"

**Solution future :** Implémenter une persistance du cache (v2.0).

### ⏱️ Performance

Le scan Nmap peut être **long** sur de grandes plages IP :

| Plage | Temps estimé |
|-------|--------------|
| /24 (256 IPs) | 5-15 minutes |
| /16 (65536 IPs) | Plusieurs heures |

**Optimisation :** Privilégiez les scans ciblés sur des sous-réseaux spécifiques.

---

## 📊 Exemples de rapports

### Rapport HTML

Le rapport HTML généré inclut :

- 🎨 **Code couleur** par statut (rouge, orange, vert)
- 📋 **Tableau trié** par criticité
- 📈 **Statistiques** : nombre d'OS par statut
- 🖨️ **Prêt à l'impression** pour documentation

### Rapport JSON

Structure du JSON :

```json
[
  {
    "ip": "192.168.1.10",
    "hostname": "SRV-DC01",
    "os": "Windows Server",
    "version": "2012 R2",
    "eol": "2023-10-10",
    "status": "NON SUPPORTÉ"
  }
]
```

### Rapport CSV

Colonnes du CSV :

```
IP | Hostname/CN | OS | Version | EOL | Statut
```

Import direct dans Excel, Power BI, ou bases de données.

---

## 🛠️ Dépannage

### Erreurs courantes et solutions

| Erreur | Cause | Solution |
|--------|-------|----------|
| `SSL: CERTIFICATE_VERIFY_FAILED` | Bug Python Windows avec certificats | **Ajouter les 3 lignes du fix SSL** (voir section dédiée) |
| `[sslcert: CERTIFICATE_VERIFY_FAILED]` | Certificats auto-signés sur serveurs cibles | **NORMAL** - Ignorez, la détection OS fonctionne |
| `nmap: command not found` | Nmap non installé | Installer Nmap (`apt install nmap` ou depuis nmap.org) |
| `Permission denied` | Pas de droits admin | Lancer en **root/Administrateur** |
| `Timeout after 30 minutes` | Réseau lent ou plage IP trop large | Réduire la plage IP (`/24` max recommandé) |
| `Fichier CSV introuvable` | Mauvais chemin ou nom de fichier | Vérifier le chemin complet ou copier le CSV dans le dossier output |
| `Version non détectée par Nmap` | Limitation Linux | Vérification manuelle via `cat /etc/os-release` |

### Debug mode

Pour plus de verbosité, ajoutez des prints dans les fonctions critiques :

```python
# Dans get_eol_from_api()
print(f"[DEBUG] API call: {url}")
print(f"[DEBUG] Response: {data}")
```

---

## 🗺️ Roadmap

### Version 2.0 (En cours)

- [ ] **Persistance du cache** API (fichier JSON local)
- [ ] **Support agents SSH** pour détection Linux précise
- [ ] **Export PDF** avec graphiques
- [ ] **Planificateur** de scans périodiques (cron/scheduled tasks)
- [ ] **Dashboard web** Flask/Django pour consultation

### Version 3.0 (Futur)

- [ ] **Base de données** (SQLite/PostgreSQL) pour historique
- [ ] **Alerting** par email/Slack/Teams
- [ ] **API REST** pour intégration CMDB
- [ ] **Multi-threading** pour scans plus rapides
- [ ] **Support containers** (Docker/Kubernetes)

### Contributions bienvenues !

Vous avez des idées ? Ouvrez une **issue** ou proposez une **pull request** !

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment participer :

### 1. Fork le projet

```bash
git clone https://github.com/votre-username/audit-obsolescence-reseau.git
```

### 2. Créer une branche

```bash
git checkout -b feature/amelioration-detection-linux
```

### 3. Commiter vos changements

```bash
git commit -m "Ajout détection Ubuntu via SSH"
```

### 4. Pusher vers votre fork

```bash
git push origin feature/amelioration-detection-linux
```

### 5. Ouvrir une Pull Request

Décrivez clairement les changements et leur bénéfice.

### 🐛 Signaler un bug

Utilisez les **issues** GitHub avec le template :

```
**Description du bug**
[Description claire]

**Étapes pour reproduire**
1. Lancer le script avec...
2. Entrer la plage...
3. Observer l'erreur...

**Comportement attendu**
[Ce qui devrait se passer]

**Environnement**
- OS: Windows Server 2019
- Python: 3.9
- Nmap: 7.92
- Fix SSL appliqué: Oui/Non
```

---

## 📜 Licence

Ce projet est sous licence **MIT**. Vous êtes libre de :

- ✅ Utiliser commercialement
- ✅ Modifier le code
- ✅ Distribuer
- ✅ Utiliser en privé

Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- **Nmap** - [nmap.org](https://nmap.org) - L'outil de scan réseau de référence
- **endoflife.date** - [endoflife.date](https://endoflife.date) - API gratuite de dates EOL
- **Communauté Python** - Pour les excellentes bibliothèques standard
- **Let's Encrypt** - Pour les certificats SSL gratuits (même si Python Windows a du mal avec 😅)

---

## 📞 Contact & Support

- 📧 **Email** : votre-email@example.com
- 💬 **Issues** : [GitHub Issues](https://github.com/votre-repo/audit-obsolescence-reseau/issues)
- 📖 **Wiki** : [Documentation complète](https://github.com/votre-repo/audit-obsolescence-reseau/wiki)

---

<div align="center">

**⭐ Si ce projet vous est utile, n'hésitez pas à lui donner une étoile ! ⭐**

*Fait avec ❤️ par l'équipe Infrastructure - Testé sur Windows, Linux et macOS*

**🔧 N'oubliez pas le fix SSL sur Windows ! 🔧**

</div>
