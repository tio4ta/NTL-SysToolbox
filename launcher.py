#!/usr/bin/env python3

import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SCRIPTS = {
    "1": {
        "name": "Diagnostic",
        "path": os.path.join(BASE_DIR, "Diagnostic", "diag.py"),
        "type": "python"
    },
    "2": {
        "name": "WMS - Backup",
        "path": os.path.join(BASE_DIR, "Backup", "wms.py"),
        "type": "python"
    },
    "3": {
        "name": "Audit Obsolescence",
        "path": os.path.join(BASE_DIR, "Obsolescence", "audit.py"),
        "type": "python"
    }
}


def afficher_menu():
    print("\n===== NTL SysToolbox =====")
    for key, value in SCRIPTS.items():
        print(f"{key} - {value['name']}")
    print("Q - Quitter")


def lancer_script(choix):
    script = SCRIPTS[choix]

    if not os.path.exists(script["path"]):
        print("Script introuvable :", script["path"])
        return

    try:
        if script["type"] == "python":
            subprocess.run([sys.executable, script["path"]])
        elif script["type"] == "bash":
            subprocess.run(["bash", script["path"]])
    except Exception as e:
        print("Erreur lors de l'exécution :", e)


def main():
    while True:
        afficher_menu()
        choix = input("Votre choix : ").strip()

        if choix == "Q":
            print("Au revoir")
            break
        elif choix in SCRIPTS:
            lancer_script(choix)
        else:
            print("Choix invalide.")


if __name__ == "__main__":

    main()

