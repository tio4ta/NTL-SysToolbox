NTL-SysToolbox : Module WMS Manager
1. Présentation
Le WMS Manager est une application Python développée pour la Direction IT de NTL. Elle a pour objectif de garantir la résilience et la portabilité des données du système de gestion d'entrepôt (WMS).

Cette solution remplace les anciens scripts d'exploitation par une architecture logicielle orientée objet, ce qui permet une maintenance simplifiée et une meilleure évolutivité du code.

2. Fonctionnalités
L'application intègre trois modules principaux :

Sauvegarde SQL : Extraction automatisée des tables critiques (expedition, reception) via un tunnel sécurisé SSH/SFTP. Les fichiers sont horodatés et stockés localement.

Restauration : Interface interactive permettant de sélectionner une archive de sauvegarde et de la réinjecter sur le serveur de production.

Export CSV : Extraction et conversion des données via la bibliothèque Pandas pour générer des fichiers exploitables par les services logistiques et comptables.

3. Architecture Technique
L'application est conçue pour être agnostique du système d'exploitation, assurant une compatibilité totale entre les environnements Windows et Linux.

Langage : Python 3.x

Bibliothèques de communication : Paramiko (SSH/SFTP)

Traitement de données : Pandas et PyMySQL

Gestion de la configuration : Fichier JSON externe pour l'isolation des paramètres sensibles.

4. Installation
Dépendances
Les bibliothèques requises doivent être installées via le gestionnaire de paquets pip :

Bash

pip install paramiko pymysql pandas
Configuration
Le fichier Configuration.json doit être présent à la racine du projet avec la structure suivante :

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
Pour lancer l'interface de gestion, exécutez la commande suivante :

Bash

python WMSManager.py
Un menu en ligne de commande s'affiche pour diriger l'utilisateur vers les différentes opérations.

6. Arborescence du projet
Voici la structure des fichiers de ton application à inclure dans ton dépôt Git :

Plaintext

NTL-SysToolbox/
├── WMSManager.py          # Code source principal (logique métier)
├── Configuration.json     # Paramètres de connexion et chemins
├── backups/               # Dossier local de stockage des fichiers .sql
└── README.md              # Documentation technique
