NTL-SysToolbox : Module WMS Manager
1. Présentation
Le WMS Manager est une application Python développée pour la Direction IT de Nord Transit Logistics (NTL). Elle a pour objectif de garantir la résilience et la portabilité des données du système de gestion d'entrepôt (Warehouse Management System).

Cette solution logicielle industrialise les vérifications d'exploitation et sécurise la gestion des sauvegardes de la base de données métier. En adoptant une architecture orientée objet, elle remplace les anciens scripts par un outil plus robuste, facilitant la maintenance et l'évolution future du code.

2. Fonctionnalités
L'application intègre les trois modules principaux demandés dans le cahier des charges:


Sauvegarde SQL : Extraction automatisée des tables critiques (expedition, reception) via un tunnel sécurisé SSH/SFTP.


Restauration Assistée : Interface interactive permettant de sélectionner une archive de sauvegarde locale et de la réinjecter sur le serveur de production.


Export Business Intelligence (CSV) : Extraction et conversion des données via la bibliothèque Pandas pour générer des fichiers exploitables par les services logistiques.

3. Architecture Technique
Conformément aux exigences, l'application est agnostique du système d'exploitation, assurant une compatibilité totale entre les environnements Windows et Linux.

Langage : Python 3.x.

Communication : Paramiko pour les échanges SSH/SFTP sécurisés.

Traitement de données : Pandas et PyMySQL pour l'extraction et la conversion.


Configuration : Utilisation d'un fichier Configuration.json externe pour isoler les paramètres sensibles et faciliter le déploiement.

4. Installation
Dépendances
Les bibliothèques requises doivent être installées via le gestionnaire de paquets pip :

Bash

pip install paramiko pymysql pandas
Configuration
Le fichier Configuration.json doit être présent à la racine du projet. Voici l'exemple de configuration pour l'infrastructure NTL :

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
L'outil s'utilise au travers d'un menu CLI interactif. Pour lancer l'interface, exécutez :

Bash

python WMSManager.py

6. Arborescence du projet
Structure des fichiers incluse dans le dépôt Git:

Plaintext

NTL-SysToolbox/
├── WMSManager.py          # Code source principal (logique métier)
├── Configuration.json     # Paramètres de connexion et chemins
├── backups/               # Dossier local de stockage des fichiers .sql
└── README.md              # Documenta
