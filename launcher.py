#!/usr/bin/env python3

import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SCRIPTS = {
    "1": {
        "name": "Diag - module_diag.py",
        "path": os.path.join(BASE_DIR, "Diag", "main.py"),
        "type": "python"
    },
    "2": {
        "name": "WMS - ntl_tool.sh",
        "path": os.path.join(BASE_DIR, "WMS", "ntl_tool.sh"),
        "type": "bash"
    },
    "3": {
        "name": "Audit Obsolescence - audit_os_V4.py",
        "path": os.path.join(BASE_DIR, "Audit_obsolescence", "audit_os_V4.py"),
        "type": "python"
    }
}


def afficher_menu():
    print("\n===== NTL SysToolbox =====")
    for key, value in SCRIPTS.items():
        print(f"{key} - {value['name']}")
    print("0 - Quitter")


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

        if choix == "0":
            print("Au revoir")
            break
        elif choix in SCRIPTS:
            lancer_script(choix)
        else:
            print("Choix invalide.")


if __name__ == "__main__":

    main()
