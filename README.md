# NTL-SysToolbox - Module 1 : Diagnostic Système

## Table des matières

1. Vue d'ensemble
2. Fonctionnalités
3. Vue utilisateur
4. Architecture
5. Prérequis
6. Bibliothèques Python
7. Installation
8. Configuration
9. Utilisation
    
---

## Vue d'ensemble
**NTL-SysToolbox** est un utilitaire en ligne de commande (CLI) conçu pour la Direction des Systèmes d'Information (DSI) de **Nord Transit Logistics (NTL)**, une PME de logistique implantée dans les Hauts-de-France. 

Dans un contexte de forte dépendance aux services centraux et de fenêtres de maintenance réduites, cet outil a pour but d'industrialiser les vérifications d'exploitation.Ce dépôt documente le **Module 1 : Diagnostic**, dont l'objectif est de confirmer rapidement que les briques critiques du siège sont disponibles et cohérentes, tout en produisant un état synthétique des serveurs. L'outil est développé pour être exécutable indifféremment sous Windows et Linux.

---

## Fonctionnalités
Conformément au cahier des charges, le module de diagnostic couvre les périmètres suivants :
* **Contrôle de l'Infrastructure Identité & Résolution :** Vérification de l'état des services Active Directory et DNS sur les contrôleurs de domaine.
* **Contrôle de la Base de Données Métier :** Test du bon fonctionnement de la base de données MySQL du système de gestion d'entrepôt (WMS).
* **Audit des Serveurs Windows :** Récupération de la version d'OS, de l'uptime, et de l'utilisation des ressources CPU/RAM/Disques pour une machine Windows Server.
* **Audit des Serveurs Linux (Ubuntu) :** Récupération de la version d'OS, de l'uptime, et de l'utilisation des ressources CPU/RAM/Disques pour une machine Ubuntu.
* **Formatage Standardisé :** Les sorties sont lisibles par un humain et disponibles en format structuré (JSON, horodatées), avec des codes de retour exploitables en supervision.

---

## Vue utilisateur
L'outil s'utilise au travers d'un menu CLI interactif permettant de lancer les différentes fonctions et demandant les arguments nécessaires à l'exécution de ces dernières.

L'expérience utilisateur se veut fluide et sécurisée :
* **Menu de navigation clair :** Un affichage épuré permettant de sélectionner précisément le test à effectuer.
* **Sécurité des saisies :** Lors de l'interrogation de serveurs distants, les mots de passe saisis par l'opérateur sont masqués à l'écran.
* **Autonomie :** La DSI peut déployer l'outil sur une machine standard et l'utiliser sans assistance grâce à un paramétrage simplifié.

---

## Architecture
L'architecture du script repose sur un modèle modulaire et *Agentless* (sans agent installé sur les cibles) :
* **Logique de séparation :** Le code sépare l'interface utilisateur (Menu CLI) de la logique métier.
* **Mode *Agentless* :** L'outil utilise des protocoles standards de l'industrie pour interroger les serveurs distants :
  * **WinRM (Windows Remote Management)** pour l'exécution de scripts PowerShell sur les serveurs Microsoft.
  * **SSH (Secure Shell)** pour l'exécution de commandes Bash sur les environnements Linux.

---

## Prérequis
Pour déployer et exécuter NTL-SysToolbox, l'environnement doit respecter les éléments suivants :
* **Système d'exploitation :** Windows ou Linux.
* **Moteur d'exécution :** Python 3.8 ou supérieur.
* **Réseau :** Accès réseau ouvert vers les cibles sur les ports 53 (DNS), 389 (LDAP), 3306 (MySQL/MariaDB), 22 (SSH), et 5985 (WinRM HTTP).
* **Cibles Windows :** Le service WinRM doit être activé (`Enable-PSRemoting -Force`).
* **Cibles Ubuntu :** Le service OpenSSH-Server doit être actif.

---

## Bibliothèques Python
Le projet s'appuie sur des bibliothèques robustes :
* `pymysql` : Connecteur pour interagir avec les bases de données MySQL et MariaDB.
* `paramiko` : Implémentation du protocole SSH pour l'exécution de commandes distantes.
* `pywinrm` : Client permettant d'interagir avec WinRM pour piloter les serveurs Microsoft.
* *Modules standards :* `json`, `os`, `sys`, `socket`, `datetime`, `getpass`.

---

## Installation

Le projet doit être livré dans un dépôt Git propre, avec un historique lisible et des branches de travail isolées.

1. **Cloner le dépôt :**
   ```Bash
   git clone <URL_DU_DEPOT_GIT>
   cd NTL-SysToolbox

2. **Installer les paquets Python requis :**
   ```Bash
   pip install pymysql paramiko pywinrm

## 🔧 Configuration

La configuration tient dans un fichier simple, surchargeable par variables d'environnement.

Créez un fichier nommé config.json à la racine de l'exécutable pour automatiser les tests AD et SQL. 

Voici un exemple de configuration :

   {
    "DC_IP": "192.168.10.10",
    "MYSQL_HOST": "192.168.10.21",
    "MYSQL_USER": "root",
    "MYSQL_PASSWORD": "VotreMotDePasse",
    "MYSQL_DB": "wms_db"
   }

## Utilisation

Avec ces éléments, la DSI doit pouvoir déployer l'outil sur une machine standard et l'utiliser sans assistance

1. **Lancez l'outil au travers de son interface interactive: **
   ```Bash
   pip install pymysql paramiko pywinrm

2. **Un menu s'affiche à l'écran. Saisissez le numéro correspondant au test souhaité (1 à 4).**

3. **Pour les tests sur les serveurs distants (Options 3 et 4), l'outil vous demandera l'adresse IP de la cible ainsi que vos identifiants administrateurs. Ces derniers sont masqués lors de la frappe pour des raisons de sécurité.**

## Exemple de résultat (JSON)
Toutes les exécutions produisent des sorties horodatées, lisibles, avec des codes de retour exploitables. Voici un exemple de sortie pour le diagnostic d'un serveur Ubuntu :

```JSON
{
    "timestamp": "2026-02-24T10:15:30.123456+00:00",
    "module": "Metrics Ubuntu (SSH)",
    "global_status": "OK",
    "data": {
        "declared_target_ip": "192.168.10.22",
        "expected_os": "Ubuntu",
        "os_version": "Ubuntu 20.04.6 LTS",
        "uptime": "up 2 weeks, 3 days, 4 hours, 12 minutes",
        "cpu_load": "18.5%",
        "ram_usage": "62.1%",
        "disk_usage": "45%"
    }
}
