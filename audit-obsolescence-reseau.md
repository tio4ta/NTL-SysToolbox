# Module d'audit d'obsolescence réseau

Ce script Python réalise un audit d'obsolescence des systèmes d'exploitation détectés sur un réseau, en se basant sur un scan Nmap et sur les dates de fin de support publiées sur le site endoflife.date via son API.

## Objectifs du script

1. **Découvrir les hôtes** d'une plage réseau et identifier leur OS (Windows, Windows Server, Ubuntu, Debian, Linux générique) grâce à Nmap.

2. **Vérifier pour chaque OS** s'il est encore supporté, en fin de vie imminente ou déjà hors support, via l'API endoflife.date.

3. **Générer automatiquement des rapports** exploitables (CSV, JSON, HTML) pour documenter l'état d'obsolescence du parc.

Ce module a évolué au fil de plusieurs versions : gestion d'un cache pour l'API, amélioration de la détection d'OS, prise en charge d'un import CSV existant, ajout d'un rapport HTML plus lisible, et mise en place d'un menu interactif pour l'utiliser sans modifier le code.

## Pourquoi Nmap ?

Nmap est utilisé car c'est un outil largement reconnu pour la découverte réseau et la détection de systèmes d'exploitation et de services, avec des options avancées comme la détection d'OS (`-O`) et de version de services (`-sV`).

Le script lance Nmap avec les options suivantes :

- `-O` : détection d'OS
- `-sV` : détection de versions de services
- `--osscan-guess` : améliore les « meilleurs efforts » lorsque Nmap n'est pas sûr de l'OS exact
- `--script ssl-cert` : récupère le certificat SSL pour extraire éventuellement le Common Name (CN)

Le choix de Nmap permet de rester non intrusif (scan réseau passif du point de vue des systèmes scannés) et de ne pas nécessiter d'agent sur les machines cibles.

## Limites sur les versions Linux

La détection précise de la version d'une distribution Linux via un simple scan réseau est très limitée : Nmap se base sur des empreintes réseau (stack TCP/IP, réponses aux sondes, bannières de services), ce qui permet souvent d'identifier « Linux » mais pas la version exacte d'Ubuntu/Debian ou du kernel.

Pour Linux, la méthode fiable consiste à interroger directement la machine (par exemple via `cat /etc/os-release`), ce que ce script ne peut pas faire puisqu'il travaille uniquement à partir d'un scan réseau.

C'est pour cela que :

- Les OS Linux génériques remontés par Nmap sont indiqués comme « Linux – Version non détectée par Nmap ».
- Le script signale explicitement qu'une vérification manuelle est nécessaire pour ces cas.

## Fonctionnement global

1. **Scan réseau** d'une plage IP avec Nmap et export en XML.
2. **Parsing du fichier XML** pour reconstruire une liste d'hôtes avec : IP, hostname/CN, OS, version.
3. **Normalisation** de l'OS et de la version (Windows, Windows Server, Ubuntu, Debian, Linux).
4. **Appel à l'API endoflife.date** pour chaque couple OS/version afin de récupérer les dates de support et EOL.
5. **Calcul du statut** : SUPPORTÉ, EOL < 1 AN, EOL IMMINENT, NON SUPPORTÉ, ou cas particuliers (version inconnue, non détectable).
6. **Affichage console** + génération de rapports CSV/JSON/HTML dans un dossier de sortie.

## Présentation des principaux blocs du script

### 1. Configuration globale

- **OUTPUT_DIR** : dossier de sortie des fichiers (scan.xml, rapports CSV/JSON/HTML)
- **EOL_CACHE** : cache en mémoire pour éviter d'appeler plusieurs fois l'API endoflife.date pour la même version

### 2. Récupération des dates de fin de support (API endoflife.date)

**Fonction :** `get_eol_from_api(product, version)`

- Pré-normalisation des versions pour Windows / Windows Server (ex. 2012 R2, 2016, 10, 11, etc.)
- Mapping des noms internes (Windows, Windows Server, Ubuntu, Debian) vers les produits de l'API (windows, windows-server, ubuntu, debian)
- Téléchargement du JSON de l'API pour le produit concerné, puis recherche du cycle correspondant à la version demandée
- Renvoi de la date de fin de support et/ou de la date EOL, avec mise en cache du résultat dans `EOL_CACHE` pour optimiser les appels suivants

### 3. Scan réseau avec Nmap

**Fonction :** `scan_network(network)`

- Construction de la commande Nmap avec les options d'OS detection, de version de services, de script ssl-cert et d'export XML (`-oX scan.xml`)
- Exécution de Nmap via `subprocess.run` avec un timeout de 30 minutes
- Passage du fichier XML généré à la fonction `parse_xml` pour extraire les informations hôte par hôte

### 4. Analyse du XML Nmap et extraction OS/hostname

**Fonction :** `parse_xml(xml_file)`

- Parcours des nœuds `<host>` dont l'état est `up`
- Récupération de l'IP (adresse IPv4), du hostname si connu par Nmap, ou à défaut du Common Name du certificat SSL (via `extract_common_name`)
- Récupération des blocs d'OS détectés (`osmatch`), puis normalisation de la chaîne brute de Nmap grâce à `extract_os`

**Fonction :** `extract_os(os_string)`

- Détection de Debian/Ubuntu par motif, avec extraction de la version si possible
- Détection des versions Windows Desktop (XP, Vista, 7, 8, 8.1, 10, 11)
- Détection des versions Windows Server (2003, 2008, 2012, 2016, 2019, 2022, avec gestion de R2)
- Cas Linux générique : renvoi « Linux – Version non détectée par Nmap » pour signaler la limite de la méthode

**Fonction :** `extract_common_name(host_elem)`

- Parcourt les résultats du script ssl-cert dans le XML pour récupérer le `commonName` du certificat, utile comme hostname logique quand le nom DNS n'est pas connu

### 5. Import d'un CSV existant

**Fonction :** `import_csv(csv_file)`

- Essaye plusieurs chemins possibles (dossier courant, OUTPUT_DIR, nom de fichier simple) pour retrouver le CSV
- Lit un CSV avec des colonnes `IP`, `Hostname`, `OS_Name`, `OS_Version`, et reconstruit la liste d'hôtes dans le même format que celui du scan Nmap
- Permet de réutiliser un inventaire existant sans refaire un scan complet

### 6. Calcul du statut d'obsolescence

**Fonction :** `get_status(os_name, version)`

- Gère les cas où l'OS ou la version sont inconnus ou non détectables (notamment Linux générique)
- Appelle `get_eol_from_api` pour obtenir la date EOL et calcule le nombre de jours restants
- Retourne un statut lisible :
  - **SUPPORTÉ**
  - **EOL < 1 AN**
  - **EOL IMMINENT**
  - **NON SUPPORTÉ**
  - Ou des messages spécifiques en cas de version inconnue/non détectable

### 7. Affichage et génération de rapports

**Fonction :** `show_hosts(hosts)`

- Affiche un tableau en console avec : IP, Hostname/CN, OS, Version, EOL, Statut
- Le statut résulte de `get_status`, ce qui permet un coup d'œil rapide sur les systèmes à risque

**Fonction :** `generate_report(hosts, base_filename="rapport")`

Génère trois fichiers dans `OUTPUT_DIR` :

- **CSV** : pour exploitation dans Excel/Power BI
- **JSON** : pour intégration dans d'autres outils/scripts
- **HTML** : rapport lisible dans un navigateur avec un code couleur (badges) en fonction du statut

### 8. Listing des versions d'un OS

**Fonction :** `list_all_versions(os_name)`

- Interroge l'API endoflife.date pour un OS donné (Windows, Windows Server, Ubuntu, Debian) et affiche les principaux cycles avec leurs dates de support et EOL
- Donne un aperçu rapide des versions encore actives ou déjà terminées

### 9. Menu interactif

**Fonction :** `menu()`

Propose une interface en ligne de commande avec les options suivantes :

1. Scanner réseau
2. Importer un CSV
3. Afficher les hôtes
4. Lister les versions d'un OS
5. Générer un rapport
6. Quitter

C'est le point d'entrée principal (`if __name__ == "__main__": menu()`), ce qui permet d'utiliser le script comme un petit outil interactif sans modifier le code.

## Utilisation

Le script s'utilise en lançant simplement :

```bash
python audit_obsolescence.py
```

Puis en naviguant dans le menu interactif pour :

- Scanner un réseau (nécessite les droits root/admin pour Nmap)
- Importer un inventaire CSV existant
- Consulter les résultats
- Générer des rapports exploitables

## Dépendances

- Python 3.x
- Nmap installé sur le système
- Accès à internet pour interroger l'API endoflife.date
- Bibliothèques Python : `subprocess`, `xml.etree.ElementTree`, `json`, `csv`, `datetime`, `urllib.request`

## Remarques importantes

- **Droits d'exécution** : Le scan Nmap avec l'option `-O` nécessite généralement des privilèges root/administrateur
- **Performance** : Le scan peut prendre du temps sur de grandes plages IP
- **Limitations Linux** : La détection de versions précises pour les distributions Linux est limitée par les capacités de Nmap en scan réseau
- **Cache API** : Le cache en mémoire optimise les appels multiples mais est réinitialisé à chaque exécution du script

## Évolutions futures possibles

- Persistance du cache API entre les exécutions
- Intégration de méthodes de détection complémentaires pour Linux (SSH, agents)
- Exports supplémentaires (PDF, bases de données)
- Planification automatique des scans périodiques
- Dashboard web pour consultation des rapports