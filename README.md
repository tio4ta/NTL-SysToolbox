# NTL-SysToolbox - Module 1 : Diagnostic Système

## 📑 Table des matières
1. [Vue d'ensemble](#vue-densemble)
2. [Fonctionnalités](#fonctionnalités)
3. [Vue utilisateur](#vue-utilisateur)
4. [Architecture](#architecture)
5. [Prérequis](#prérequis)
6. [Bibliothèques Python](#bibliothèques-python)
7. [Installation](#installation)
8. [Configuration](#configuration)
9. [Utilisation](#utilisation)

---

## 🌍 Vue d'ensemble
[cite_start]**NTL-SysToolbox** est un utilitaire en ligne de commande (CLI) conçu pour la Direction des Systèmes d'Information (DSI) de **Nord Transit Logistics (NTL)**, une PME de logistique implantée dans les Hauts-de-France[cite: 32]. 

[cite_start]Dans un contexte de forte dépendance aux services centraux et de fenêtres de maintenance réduites, cet outil a pour but d'industrialiser les vérifications d'exploitation[cite: 90]. [cite_start]Ce dépôt documente le **Module 1 : Diagnostic**, dont l'objectif est de confirmer rapidement que les briques critiques du siège sont disponibles et cohérentes, tout en produisant un état synthétique des serveurs[cite: 94]. [cite_start]L'outil est développé pour être exécutable indifféremment sous Windows et Linux[cite: 91].

---

## ✨ Fonctionnalités
Conformément au cahier des charges, le module de diagnostic couvre les périmètres suivants :
* [cite_start]**Contrôle de l'Infrastructure Identité & Résolution :** Vérification de l'état des services Active Directory et DNS sur les contrôleurs de domaine[cite: 96].
* [cite_start]**Contrôle de la Base de Données Métier :** Test du bon fonctionnement de la base de données MySQL du système de gestion d'entrepôt (WMS)[cite: 63, 97].
* [cite_start]**Audit des Serveurs Windows :** Récupération de la version d'OS, de l'uptime, et de l'utilisation des ressources CPU/RAM/Disques pour une machine Windows Server[cite: 98].
* [cite_start]**Audit des Serveurs Linux (Ubuntu) :** Récupération de la version d'OS, de l'uptime, et de l'utilisation des ressources CPU/RAM/Disques pour une machine Ubuntu[cite: 99].
* [cite_start]**Formatage Standardisé :** Les sorties sont lisibles par un humain et disponibles en format structuré (JSON, horodatées), avec des codes de retour exploitables en supervision[cite: 92, 117].

---

## 👤 Vue utilisateur
[cite_start]L'outil s'utilise au travers d'un menu CLI interactif permettant de lancer les différentes fonctions et demandant les arguments nécessaires à l'exécution de ces dernières[cite: 119].

L'expérience utilisateur se veut fluide et sécurisée :
* **Menu de navigation clair :** Un affichage épuré permettant de sélectionner précisément le test à effectuer.
* **Sécurité des saisies :** Lors de l'interrogation de serveurs distants, les mots de passe saisis par l'opérateur sont masqués à l'écran.
* [cite_start]**Autonomie :** La DSI peut déployer l'outil sur une machine standard et l'utiliser sans assistance grâce à un paramétrage simplifié[cite: 118].

---

## 🏗️ Architecture
L'architecture du script repose sur un modèle modulaire et *Agentless* (sans agent installé sur les cibles) :
* **Logique de séparation :** Le code sépare l'interface utilisateur (Menu CLI) de la logique métier.
* **Mode *Agentless* :** L'outil utilise des protocoles standards de l'industrie pour interroger les serveurs distants :
  * **WinRM (Windows Remote Management)** pour l'exécution de scripts PowerShell sur les serveurs Microsoft.
  * **SSH (Secure Shell)** pour l'exécution de commandes Bash sur les environnements Linux.

---

## ⚙️ Prérequis
Pour déployer et exécuter NTL-SysToolbox, l'environnement doit respecter les éléments suivants :
* [cite_start]**Système d'exploitation :** Windows ou Linux[cite: 91].
* **Moteur d'exécution :** Python 3.8 ou supérieur.
* **Réseau :** Accès réseau ouvert vers les cibles sur les ports 53 (DNS), 389 (LDAP), 3306 (MySQL/MariaDB), 22 (SSH), et 5985 (WinRM HTTP).
* **Cibles Windows :** Le service WinRM doit être activé (`Enable-PSRemoting -Force`).
* **Cibles Ubuntu :** Le service OpenSSH-Server doit être actif.

---

## 📚 Bibliothèques Python
Le projet s'appuie sur des bibliothèques robustes :
* `pymysql` : Connecteur pour interagir avec les bases de données MySQL et MariaDB.
* `paramiko` : Implémentation du protocole SSH pour l'exécution de commandes distantes.
* `pywinrm` : Client permettant d'interagir avec WinRM pour piloter les serveurs Microsoft.
* *Modules standards :* `json`, `os`, `sys`, `socket`, `datetime`, `getpass`.

---

## 📥 Installation

[cite_start]Le projet doit être livré dans un dépôt Git propre, avec un historique lisible et des branches de travail isolées[cite: 115].

1. **Cloner le dépôt :**
   ```bash
   git clone <URL_DU_DEPOT_GIT>
   cd NTL-SysToolbox
