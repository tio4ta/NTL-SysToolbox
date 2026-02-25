NTL-SysToolbox : Module WMS Manager
1. Présentation
Le WMS Manager est une application Python développée pour la DSI de NTL. Elle permet de garantir la résilience et la portabilité des données du système d'entrepôt (WMS) de manière automatisée et sécurisée.

L'application remplace les anciens scripts d'exploitation par une solution orientée objet, facilitant la maintenance et l'évolution du code.

2. Fonctionnalités clés
L'application propose trois modes opératoires principaux :

Backup SQL : Extraction automatique des tables critiques (expedition, reception) via SSH/SFTP et stockage local horodaté.

Restauration Assistée : Menu interactif permettant de choisir un point de restauration et de le réinjecter sur le serveur de production.

Export Business Intelligence (CSV) : Extraction directe des données via le moteur Pandas pour générer des fichiers CSV exploitables par la direction (comptabilité, logistique).

3. Architecture Technique
L'application est conçue pour être agnostique de l'OS (compatible Windows et Linux).

Technologies utilisées :
Langage : Python 3.x

Communication Serveur : Paramiko (SSH/SFTP) pour les échanges sécurisés.

Traitement de données : Pandas & PyMySQL pour l'extraction SQL et la conversion CSV.

Configuration : Fichier Configuration.json pour séparer le code des données sensibles (identifiants, IP).

4. Installation & Préparation
Prérequis
Bash

pip install paramiko pymysql pandas
Configuration
Modifier le fichier Configuration.json à la racine du projet :

JSON

{
  "ssh": {
    "host": "10.5.70.50",
    "user": "user",
    "pass": "votre_mot_de_passe"
  },
  "db": {
    "user": "admin_ntl",
    "pass": "Ntl2026!",
    "name": "ntl_wms"
  },
  "paths": {
    "local_backup_dir": "./backups"
  }
}
5. Utilisation
L'application se lance via un terminal (PowerShell sur Windows ou Bash sur Linux) :

Bash

python WMSManager.py
Un menu interactif s'affiche alors pour guider l'utilisateur.

Pourquoi c'est mieux pour ton oral (Arguments à sortir au jury) :
La Sécurité : "Contrairement à un script classique, mon application utilise des bibliothèques comme Paramiko qui gèrent proprement les tunnels SSH, évitant de laisser traîner des fichiers temporaires non sécurisés."

La Portabilité : "Grâce à la bibliothèque pathlib et au test platform.system(), mon application détecte seule si elle est sur Windows ou Linux et ajuste les dossiers de sortie (Documents ou Home) automatiquement."

La Valeur Métier : "L'ajout du module CSV via Pandas montre que l'outil ne sert pas qu'aux techniciens, mais permet aussi de fournir des rapports de données directement exploitables par les services logistiques de NTL."

L'Évolutivité : "Le code est découpé en classes et méthodes. Si demain NTL change de base de données (ex: vers PostgreSQL), il suffit de modifier une méthode sans réécrire toute l'application."
