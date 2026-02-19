#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'Audit d'Obsolescence Réseau
"""

import subprocess
import re
import csv
import json
import os
from datetime import datetime


def scan_host(target):
    """
    Lance un scan Nmap avec détection d'OS.
    """
    cmd = ["nmap", "-O", "--osscan-guess", target]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"Erreur lors du scan : {e}")
        return None


def extract_os_info(nmap_output):
    """
    Extrait les informations d'OS depuis la sortie Nmap.
    """
    if not nmap_output:
        return None

    match = re.search(r"OS details: (.*)", nmap_output)
    if match:
        return match.group(1)

    return "OS non identifié"


def generate_report(data, filename="rapport_audit.json"):
    """
    Génère un rapport JSON.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def main():
    target = input("Entrez l'adresse IP ou le hostname : ")

    print("Scan en cours...")
    output = scan_host(target)

    os_info = extract_os_info(output)

    report = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cible": target,
        "os_detecte": os_info
    }

    generate_report(report)

    print("Audit terminé. Rapport généré.")


if __name__ == "__main__":
    main()
