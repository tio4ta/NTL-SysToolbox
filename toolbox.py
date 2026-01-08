#!/usr/bin/env python3
import click
import json
import csv
import os
from datetime import datetime
from tabulate import tabulate
import nmap

EOL_DB = {
    "Ubuntu 20.04": "2025-05-01",
    "CentOS": "2024-06-30",
    "Windows Server 2016": "2027-01-11",
    "Windows Server 2019": "2029-01-09",
    "Windows 10": "2025-10-14",
    "Windows 7": "2020-01-14",
    "VMware ESXi 6.5": "2024-10-15",
    "Windows 11": "2031-10-14"
}

def scan_reseau(plage="192.168.10.0/24"):
    nm = nmap.PortScanner()
    try:
        nm.scan(plage, arguments='-O -sV --top-ports 1000')
        composants = []
        for host in nm.all_hosts():
            if nm[host].state() == 'up':
                os_info = nm[host].get('osclass', [{}])[0].get('name', 'Inconnu')
                services = ', '.join([s.get('name', '') for s in nm[host].get('tcp', {}).values()])
                composants.append({'IP': host, 'OS_detecte': os_info, 'Services': services[:50]})
        return composants
    except Exception as e:
        print(f"Erreur scan: {e}")
        return []

@click.group()
def cli():
    os.makedirs("output", exist_ok=True)

@cli.command()
@click.option('--plage', default='192.168.10.0/24')
@click.option('--csv-input', help='CSV ip,os_version')
@click.option('--os-seul', help='OS ex: Ubuntu')
def audit(plage, csv_input, os_seul):
    today = datetime.now().date()
    results = []
    
    if os_seul:
        versions = {k: v for k, v in EOL_DB.items() if os_seul.lower() in k.lower()}
        print(f"Versions {os_seul}:")
        print(tabulate(versions.items(), headers=['Version', 'EOL']))
        return
    
    if csv_input and os.path.exists(csv_input):
        with open(csv_input, 'r') as f:
            reader = csv.DictReader(f)
            composants = [{'IP': row['ip'], 'OS_detecte': row['os_version']} for row in reader]
    else:
        print(f"Scan {plage}...")
        composants = scan_reseau(plage)
    
    for comp in composants:
        os_ver = comp['OS_detecte']
        eol_date = EOL_DB.get(os_ver, "Inconnu")
        status = "Supporté"
        if eol_date != "Inconnu":
            eol = datetime.strptime(eol_date, "%Y-%m-%d").date()
            if today > eol:
                status = "Obsolète"
            elif (eol - today).days < 180:
                status = "Bientôt"
        results.append({**comp, 'EOL': eol_date, 'Status': status})
    
    print("\nRAPPORT AUDIT:")
    print(tabulate(results, headers="keys"))
    
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = f"output/audit_{ts}.json"
    csv_file = f"output/audit_{ts}.csv"
    
    with open(json_file, 'w') as f:
        json.dump({'timestamp': ts, 'plage': plage, 'results': results}, f, indent=2)
    with open(csv_file, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    exit_code = 2 if any(r['Status'] == 'Obsolète' for r in results) else 0
    print(f"Fichiers: {json_file} {csv_file} (code:{exit_code})")
    raise click.Abort(exit_code)

if __name__ == "__main__":
    cli()
