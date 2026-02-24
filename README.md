DOSSIER D’EXPLOITATION TECHNIQUE : MODULE DE RÉSILIENCE WMS 

1. Contexte, Enjeux et Objectifs du Projet 

L'entreprise NTL, acteur majeur de la logistique, s'appuie sur une base de données MariaDB pour son Warehouse Management System (WMS). Ce système est le cœur névralgique de l'activité : il orchestre en temps réel les flux, l'inventaire et les ordres de préparation. 

La Problématique : Une indisponibilité de ce serveur entraînerait une paralysie totale de l'entrepôt. Sans données, les opérateurs ne peuvent plus identifier les colis, localiser les stocks ou gérer les expéditions, provoquant des ruptures de chaîne et des pertes financières immédiates. 

Ma Mission : Concevoir une solution de Protection et Continuité d'Activité (PCA). L'objectif n'est pas seulement de stocker des données, mais de garantir qu'elles restent exploitables en mode dégradé, assurant la survie de l'activité même lors d'une panne informatique majeure. 

2. Justification et Défense des Choix Techniques 

2.1. Choix du langage : Bash vs Python 

Le choix : Utilisation du Shell Bash (#!/bin/bash). Justification : Le Bash a été privilégié car il est le langage natif de l'administration système Linux. Il permet d'appeler directement les utilitaires système (mysqldump, scp, mutt) sans dépendances logicielles lourdes. De plus, pour respecter la contrainte d'exécution multiplateforme, le Bash est parfaitement supporté via WSL ou Git Bash sous Windows, garantissant une portabilité totale. 

2.2. Accessibilité et Continuité Métier (Le format CSV) 

Le choix : Génération systématique de fichiers CSV en complément du dump SQL. Justification approfondie : Le format SQL est une image technique destinée à une restauration sur un serveur identique. En cas de sinistre total (incendie, ransomware), reconstruire un environnement SQL complet prend du temps. Le format CSV est agnostique : il est universellement lisible sans logiciel spécifique. Impact Métier : En situation critique, un chef de quai peut ouvrir ces fichiers sur un simple ordinateur portable via Excel. Cela permet de basculer sur une gestion manuelle temporaire (pointage papier) et de maintenir les expéditions, évitant ainsi l'arrêt total du service client de NTL. 

2.3. Sécurité des flux par Chiffrement RSA 4096 

Le choix : Authentification SSH par échange de clés asymétriques. Justification approfondie : L'usage de mots de passe dans des scripts automatisés est une pratique à proscrire (risque d'interception ou de fuite). J'ai opté pour une clé RSA de 4096 bits, offrant un niveau de résistance aux attaques par brute-force de classe industrielle. Impact Technique : Ce choix permet de créer un canal de communication "sans couture" et hautement sécurisé entre le serveur de production et le serveur de repli. Le transfert est crypté de bout en bout, et l'automatisation est totale. 

2.4. Réplication Distante pour le PRA (Site de Repli) 

Le choix : Externalisation vers l'hôte distant 10.5.70.50. Justification approfondie : Une sauvegarde qui ne quitte pas le serveur source n'est pas une sécurité, c'est une copie de proximité. Ma stratégie repose sur le Plan de Reprise d'Activité (PRA) par déportation des données. Impact Stratégique : En isolant les sauvegardes sur un autre serveur physique, je protège le patrimoine de NTL contre les défaillances matérielles totales (crash disque) ou les sinistres locaux. Si le site principal tombe, le site de repli détient les données prêtes à être réactivées. 

3. Fonctionnement Détaillé du Module 

L'outil ntl_tool.sh a été conçu comme une chaîne de traitement séquentiel robuste : 

Extraction de cohérence : Le script effectue un "dump" complet pour figer l'état de la base à un instant T. 

Transformation granulaire : Il filtre spécifiquement les tables reception et expedition pour les convertir en CSV. 

Tunneling Sécurisé : Les fichiers sont téléportés via le protocole SCP au travers du tunnel SSH sécurisé. 

Audit de Restauration : Sur le serveur miroir, le script réinjecte les données. Cette étape est cruciale : elle garantit que la sauvegarde est réellement exploitable et non corrompue. 

Reporting Dynamique : Envoi d'un rapport SMTP incluant les logs et les pièces jointes pour une supervision passive par la DSI. 

4. Manuel d'Installation et d'Administration (DSI) 

4.1. Récupération des sources via Git 

La solution est versionnée pour faciliter son déploiement : git clone https://github.com/tio4ta/NTL-SysToolbox.git Le dépôt contient le script ntl_tool.sh et le fichier ntl_structure.sql pour initialiser la base de données. 

4.2. Préparation de l'environnement applicatif 

L'infrastructure s'appuie sur des outils Linux standardisés : 

mutt & ssmtp : Gestionnaire de courrier et agent de transfert. 

mariadb-client : Outils natifs d'extraction de données. 

openssh-client : Moteur de transfert sécurisé. 

4.3. Sécurisation Réseau et Pare-feu (UFW) 

Afin de sécuriser les échanges tout en permettant la supervision, le pare-feu ufw a été installé et configuré : 

ufw allow 22/tcp : Autorise le tunnel SSH pour les sauvegardes. 

ufw allow 3306/tcp : Autorise les requêtes SQL (pour le monitoring). 

4.4. Configuration du canal Email (Sécurisation SMTP) 

Google impose des mesures de sécurité strictes pour les accès programmatiques. Mécanisme : Utilisation du Jeton d'application (App Password) de 16 caractères. Configuration critique : Le fichier /etc/ssmtp/ssmtp.conf doit être édité avec une précision absolue. L'absence d'espaces dans la directive AuthPass est vitale pour éviter les erreurs d'authentification (Code 535) lors de l'exécution nocturne. 

4.5. Ordonnancement de précision (Cron) 

Fréquence : 00 01 * * * (Quotidien à 01h00). Analyse du choix : Cette fenêtre horaire correspond à la période de charge d'écriture minimale sur la base MariaDB. Cela garantit un "snapshot" statique des données sans risque de verrous (locks) prolongés. 

5. Analyse des Incidents et Retours d'Expérience (Post-Mortem) 

Le développement a permis de fiabiliser le script face à des comportements systèmes spécifiques : 

Optimisation du parsing sSMTP : Détection d'échecs d'envoi liés à des caractères spéciaux mal interprétés. La configuration a été "sanitizée" pour ne contenir que des valeurs brutes. 

Correction de la syntaxe Mutt : L'usage du séparateur d'arguments -- a été implémenté pour garantir que l'adresse de destination ne soit jamais confondue avec une option de pièce jointe. 

Gestion de l'interopérabilité (Erreur 1130) : Lors des tests de monitoring depuis l'AD de mon collègue, j'ai dû modifier le bind-address sur 0.0.0.0 et accorder des privilèges spécifiques (GRANT) à l'IP de l'AD (10.5.70.10) pour permettre la remontée d'informations tout en sécurisant l'accès par pare-feu. 

6. Procédure de Vérification et Audit 

La commande de contrôle choisie est : ls -lh /backups/ntl/ 

Pourquoi cette rigueur ? * -l : Permet de vérifier les permissions (sécurité) et l'horodatage (fraîcheur de la donnée). 

-h : Le mode "Human Readable" permet à un administrateur de vérifier en une seconde si le poids du fichier est cohérent. 

 
