#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'Audit d'Obsolescence Réseau - Version améliorée
"""

import subprocess
import re
import csv
import json
import os
from datetime import datetime


# -------------------------------
# SCAN NMAP
# -------------------------------

def scan_target(target):
    """
    Lance un scan Nmap avec détection d'OS sur une IP ou plage réseau.
    """
    cmd = ["nmap", "-O", "--osscan-guess", target]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"Erreur lors du scan : {e}")
        return None


# -------------------------------
# EXTRACTION DES OS
# -------------------------------

def extract_hosts_os(nmap_output):
    """
    Extrait les IP et OS détectés depuis la sortie Nmap.
    """
    hosts_data = []
    current_ip = None

    for line in nmap_output.split("\n"):

        ip_match = re.search(r"Nmap scan report for (.*)", line)
        if ip_match:
            current_ip = ip_match.group(1)

        os_match = re.search(r"OS details: (.*)", line)
        if os_match and current_ip:
            hosts_data.append({
                "ip": current_ip,
                "os": os_match.group(1)
            })

    return hosts_data


# -------------------------------
# IMPORT BASE EOL CSV
# -------------------------------

def load_eol_database(csv_file):
    """
    Charge la base EOL depuis un fichier CSV.
    """
    eol_db = {}

    try:
        with open(csv_file, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                eol_db[row["os_name"]] = row["eol_date"]
    except Exception as e:
        print(f"Erreur chargement base EOL : {e}")

    return eol_db


# -------------------------------
# VERIFICATION OBSOLESCENCE
# -------------------------------

def check_obsolescence(os_detected, eol_db):
    """
    Compare l'OS détecté avec la base EOL.
    """
    for os_name in eol_db:
        if os_name.lower() in os_detected.lower():
            eol_date = datetime.strptime(eol_db[os_name], "%Y-%m-%d")
            status = "Supporté"

            if datetime.now() > eol_date:
                status = "Obsolète"

            return {
                "os_reference": os_name,
                "eol_date": eol_db[os_name],
                "statut": status
            }

    return {
        "os_reference": "Inconnu",
        "eol_date": "N/A",
        "statut": "Non trouvé dans la base"
    }


# -------------------------------
# GENERATION RAPPORT
# -------------------------------

def generate_json_report(data):
    filename = f"rapport_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Rapport généré : {filename}")


# -------------------------------
# MAIN
# -------------------------------

def main():

    print("=== Audit d'Obsolescence Réseau ===")

    target = input("Entrez une IP ou une plage réseau (ex: 192.168.1.0/24) : ")
    csv_file = input("Entrez le chemin du fichier CSV EOL : ")

    print("Scan en cours...")
    output = scan_target(target)

    if not output:
        print("Aucun résultat.")
        return

    hosts = extract_hosts_os(output)
    eol_db = load_eol_database(csv_file)

    results = []

    for host in hosts:
        obsolescence_info = check_obsolescence(host["os"], eol_db)

        results.append({
            "ip": host["ip"],
            "os_detecte": host["os"],
            "os_reference": obsolescence_info["os_reference"],
            "eol_date": obsolescence_info["eol_date"],
            "statut": obsolescence_info["statut"]
        })

    generate_json_report(results)

    print("Audit terminé.")


if __name__ == "__main__":
    main()
