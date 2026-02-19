#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'Audit d'Obsolescence Réseau
"""

import subprocess
import re
import csv
import os
import json
from datetime import datetime
import xml.etree.ElementTree as ET

try:
    import urllib.request
    import urllib.error
except ImportError:
    print("[!] Erreur: urllib requis")
    exit(1)

OUTPUT_DIR = r"C:\\Users\\Administrateur\\module3_audit"
EOL_CACHE = {}


def get_eol_from_api(product, version):
    """Récupère les infos EOL depuis l'API endoflife.date"""

    if product == "Windows":
        v = (version or "").lower()
        if "11" in v:
            version = "11"
        elif "10" in v:
            version = "10"
        elif "8.1" in v:
            version = "8.1"
        elif "8" in v:
            version = "8"
        elif "7" in v:
            version = "7"
        elif "xp" in v:
            version = "xp"
        elif "vista" in v:
            version = "vista"

    if product == "Windows Server":
        version = (version or "").upper().replace("R2", " R2").strip()

    product_mapping = {
        "Windows": "windows",
        "Windows Server": "windows-server",
        "Ubuntu": "ubuntu",
        "Debian": "debian"
    }

    if product not in product_mapping:
        return None, None

    api_product = product_mapping[product]
    cache_key = f"{api_product}_{version}"

    if cache_key in EOL_CACHE:
        return EOL_CACHE[cache_key]

    try:
        url = f"https://endoflife.date/api/{api_product}.json"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        for item in data:
            cycle = str(item.get('cycle', '')).strip()
            if cycle == version or cycle in str(version) or str(version) in cycle:
                eol_date = item.get('eol', None)
                support_date = item.get('support', eol_date)
                EOL_CACHE[cache_key] = (support_date, eol_date)
                return support_date, eol_date

        EOL_CACHE[cache_key] = (None, None)
        return None, None

    except Exception:
        return None, None


def scan_network(network):
    """Scan réseau avec Nmap"""
    print(f"\n[*] Scan de {network}...")
    xml_file = os.path.join(OUTPUT_DIR, "scan.xml")
    cmd = ["nmap", "-O", "-sV", "-Pn", "--osscan-guess", "--script", "ssl-cert", "-T4", "-oX", xml_file, network]

    try:
        subprocess.run(cmd, timeout=1800, check=True)
        return parse_xml(xml_file)
    except Exception as e:
        print(f"[!] Erreur scan: {e}")
        return []


def extract_os(os_string):
    """Extrait OS et version à partir de la chaîne Nmap."""
    os_lower = os_string.lower()

    if "debian" in os_lower:
        numbers = re.findall(r'\d+', os_string)
        if numbers:
            return ("Debian", numbers[0])
        return ("Debian", "Unknown")

    if "ubuntu" in os_lower:
        match = re.search(r'(\d+\.\d+)', os_string)
        if match:
            return ("Ubuntu", match.group(1))
        return ("Ubuntu", "Unknown")

    if "windows server" in os_lower:
        match = re.search(r'(2003|2008|2012|2016|2019|2022)', os_string)
        version = "Unknown"
        if match:
            version = match.group(1)
            if "r2" in os_lower:
                version += " R2"
        return ("Windows Server", version)

    if "windows" in os_lower:
        mapping = ["11", "10", "8.1", "8", "7", "vista", "xp"]
        for v in mapping:
            if v in os_lower:
                return ("Windows", v)
        return ("Windows", "Unknown")

    if "linux" in os_lower:
        return ("Linux", "Version non détectée par Nmap")

    return (os_string, "Unknown")


def extract_common_name(host_elem):
    """Extrait le commonName à partir des résultats ssl-cert."""
    for script in host_elem.findall(".//script"):
        if script.get("id") == "ssl-cert":
            for elem in script.findall(".//elem"):
                if elem.get("key") == "commonName" and elem.text:
                    return elem.text.strip()
    return None


def parse_xml(xml_file):
    """Parse le XML Nmap"""
    hosts = []

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for host in root.findall('.//host'):
            if host.find('status').get('state') != 'up':
                continue

            ip = host.find('.//address[@addrtype="ipv4"]')
            if ip is None:
                continue

            h = {'ip': ip.get('addr'), 'hostname': '', 'os': 'Unknown', 'version': 'Unknown'}

            # Hostname Nmap classique
            hostname = host.find('.//hostnames/hostname')
            if hostname is not None:
                h['hostname'] = hostname.get('name', '')

            # CommonName via SSL si pas de hostname
            if not h['hostname']:
                cn = extract_common_name(host)
                if cn:
                    h['hostname'] = cn

            # OS
            osmatches = host.findall('.//osmatch')
            if osmatches:
                for osmatch in osmatches:
                    os_raw = osmatch.get('name', '')
                    os_clean, version = extract_os(os_raw)

                    if os_clean in ["Ubuntu", "Debian"] and version == "Unknown":
                        h['os'] = os_clean
                        h['version'] = "Version non détectée par Nmap"
                        break
                    elif os_clean in ["Windows", "Windows Server", "Ubuntu", "Debian"] and version != "Unknown":
                        h['os'] = os_clean
                        h['version'] = version
                        break
                    elif h['os'] == 'Unknown':
                        h['os'] = os_clean
                        h['version'] = version

                if h['os'] == 'Unknown':
                    for osmatch in osmatches:
                        if "linux" in osmatch.get('name', '').lower():
                            h['os'] = "Linux"
                            h['version'] = "Version non détectée par Nmap"
                            break

            hosts.append(h)

    except Exception as e:
        print(f"[!] Erreur parsing: {e}")

    return hosts


def import_csv(csv_file):
    """Importe un CSV - CORRIGÉ pour ton format"""
    hosts = []

    print("\n[i] Recherche du fichier CSV...")

    paths_to_try = [
        csv_file,
        os.path.join(OUTPUT_DIR, csv_file),
        os.path.join(OUTPUT_DIR, os.path.basename(csv_file)),
        os.path.join(os.getcwd(), csv_file),
        os.path.join(os.getcwd(), os.path.basename(csv_file))
    ]

    found_path = None
    for path in paths_to_try:
        if os.path.exists(path):
            found_path = path
            print(f"[✓] Trouvé: {path}")
            break

    if not found_path:
        print(f"[!] Fichier introuvable")
        print(f"[i] Contenu de {OUTPUT_DIR}:")
        try:
            for f in os.listdir(OUTPUT_DIR):
                print(f"    - {f}")
        except:
            pass
        return []

    try:
        # Lecture directe avec délimiteur ',' (ton CSV est bien formaté)
        with open(found_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Nettoyage des valeurs
                ip = (row.get('IP') or '').strip()
                hostname = (row.get('Hostname') or '').strip()
                os_name = (row.get('OS_Name') or 'Unknown').strip()
                os_version = (row.get('OS_Version') or 'Unknown').strip()
                
                if ip:  # Seulement si IP non vide
                    hosts.append({
                        'ip': ip,
                        'hostname': hostname,
                        'os': os_name,
                        'version': os_version
                    })

        print(f"[✓] {len(hosts)} hôtes importés")
    except Exception as e:
        print(f"[!] Erreur lecture: {e}")
        # Debug: affiche les 3 premières lignes
        try:
            with open(found_path, 'r', encoding='utf-8-sig') as f:
                for i, line in enumerate(f):
                    if i < 3:
                        print(f"[DEBUG] Ligne {i}: {repr(line)}")
        except:
            pass

    return hosts


def get_status(os_name, version):
    """Retourne le statut EOL"""
    v_lower = (version or "").lower()

    if ("non détectée" in v_lower or version == "Unknown" or os_name == "Unknown"):
        if os_name in ["Linux", "Ubuntu", "Debian"]:
            return "⚠️ Version Linux non détectable par Nmap", "Vérification manuelle requise (cat /etc/os-release)"
        return "⚠️ Version non détectable", "Vérification manuelle requise"

    support_date, eol_date = get_eol_from_api(os_name, version)
    if not eol_date:
        return "❓ Version inconnue", None

    try:
        if isinstance(eol_date, bool):
            return ("✅ SUPPORTÉ" if eol_date else "❌ NON SUPPORTÉ"), ("Actif" if eol_date else "Terminé")

        eol = datetime.strptime(eol_date, '%Y-%m-%d')
        days = (eol - datetime.now()).days

        if days < 0:
            return "❌ NON SUPPORTÉ", eol_date
        elif days < 90:
            return "🔶 EOL IMMINENT", eol_date
        elif days < 365:
            return "⚡ EOL < 1 AN", eol_date
        else:
            return "✅ SUPPORTÉ", eol_date

    except:
        return "❓ Format invalide", str(eol_date)


def show_hosts(hosts):
    """Affiche les hôtes"""
    if not hosts:
        print("\n[!] Aucun hôte")
        return

    print(f"\n{'='*140}")
    print(f"{'IP':<16} {'Hostname / CN':<30} {'OS':<20} {'Version':<30} {'EOL':<15} {'Statut'}")
    print(f"{'='*140}")

    for h in hosts:
        status, eol = get_status(h['os'], h['version'])
        ip_display = h['ip']
        hostname_display = (h.get('hostname') or '')[:29]
        os_display = h['os'][:19]
        version_display = h['version'][:29] if len(h['version']) > 29 else h['version']
        eol_display = (eol or '')[:14] if eol else ''

        print(f"{ip_display:<16} {hostname_display:<30} {os_display:<20} {version_display:<30} {eol_display:<15} {status}")

    print(f"{'='*140}\n")


def generate_report(hosts, filename="rapport.html"):
    """Génère le rapport HTML"""
    if not hosts:
        print("[!] Aucun hôte")
        return

    total = len(hosts)
    unsupported = sum(1 for h in hosts if '❌' in get_status(h['os'], h['version'])[0])
    imminent = sum(1 for h in hosts if '🔶' in get_status(h['os'], h['version'])[0])
    soon = sum(1 for h in hosts if '⚡' in get_status(h['os'], h['version'])[0])
    supported = sum(1 for h in hosts if '✅' in get_status(h['os'], h['version'])[0])
    unknown = sum(1 for h in hosts if '⚠️' in get_status(h['os'], h['version'])[0] or '❓' in get_status(h['os'], h['version'])[0])

    html = f"""<!DOCTYPE html>
<html><head>
    <meta charset="UTF-8">
    <title>Rapport Audit Réseau</title>
    <style>
        body {{ font-family: Arial; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; text-align: center; margin-bottom: 10px; }}
        .subtitle {{ text-align: center; color: #666; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px; margin: 30px 0; }}
        .stat {{ text-align: center; padding: 20px; background: #f9f9f9; border-radius: 8px; border-left: 4px solid #667eea; }}
        .stat h2 {{ font-size: 2.5em; margin: 0 0 10px 0; }}
        .stat.critical {{ border-left-color: #e74c3c; }} .critical h2 {{ color: #e74c3c; }}
        .stat.warning {{ border-left-color: #f39c12; }} .warning h2 {{ color: #f39c12; }}
        .stat.good {{ border-left-color: #27ae60; }} .good h2 {{ color: #27ae60; }}
        .stat.unknown {{ border-left-color: #95a5a6; }} .unknown h2 {{ color: #95a5a6; }}
        h2 {{ color: #333; margin: 40px 0 20px 0; border-bottom: 3px solid #667eea; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
        thead {{ background: #667eea; color: white; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f9f9f9; }}
        .badge {{ padding: 6px 12px; border-radius: 20px; font-size: 0.85em; color: white; font-weight: 600; }}
        .badge-critical {{ background: #e74c3c; }} .badge-warning {{ background: #f39c12; }}
        .badge-good {{ background: #27ae60; }} .badge-unknown {{ background: #95a5a6; }}
        .note {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; border-radius: 5px; }}
    </style>
</head><body>
    <div class="container">
        <h1>📊 Rapport d'Audit d'Obsolescence Réseau</h1>
        <p class="subtitle">Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>

        <div class="stats">
            <div class="stat"><h2>{total}</h2><p>Total Composants</p></div>
            <div class="stat critical"><h2>{unsupported}</h2><p>❌ Non supportés</p></div>
            <div class="stat warning"><h2>{imminent}</h2><p>🔶 EOL imminent</p></div>
            <div class="stat warning"><h2>{soon}</h2><p>⚡ EOL proche</p></div>
            <div class="stat good"><h2>{supported}</h2><p>✅ Supportés</p></div>
            <div class="stat unknown"><h2>{unknown}</h2><p>⚠️ À vérifier</p></div>
        </div>

        <h2>📋 Inventaire Complet</h2>
        <table><thead><tr>
            <th>IP</th><th>Hostname / CN</th><th>OS</th><th>Version</th><th>Date EOL</th><th>Statut</th>
        </tr></thead><tbody>"""

    for h in hosts:
        status, eol = get_status(h['os'], h['version'])
        badge_class = 'badge-critical' if '❌' in status else 'badge-warning' if '🔶' in status or '⚡' in status else 'badge-good' if '✅' in status else 'badge-unknown'

        html += f"""
            <tr><td>{h['ip']}</td><td>{h['hostname'] or 'N/A'}</td><td>{h['os']}</td><td>{h['version']}</td><td>{eol or 'N/A'}</td><td><span class="badge {badge_class}">{status}</span></td></tr>"""

    html += """</tbody></table><p style="text-align: center; color: #666; margin-top: 40px;">
        Données EOL: <a href="https://endoflife.date" style="color: #667eea;">endoflife.date</a></p></div></body></html>"""

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    csv_path = filepath.replace('.html', '.csv')
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['IP', 'Hostname/CN', 'OS', 'Version', 'EOL', 'Statut'])
        for h in hosts:
            status, eol = get_status(h['os'], h['version'])
            writer.writerow([h['ip'], h['hostname'], h['os'], h['version'], eol or '', status])

    print(f"[✓] Rapports générés:\n    HTML: {filepath}\n    CSV:  {csv_path}")


def list_all_versions(os_name):
    """Liste toutes les versions depuis l'API"""
    product_mapping = {"Windows": "windows", "Windows Server": "windows-server", "Ubuntu": "ubuntu", "Debian": "debian"}
    if os_name not in product_mapping:
        print(f"[!] Non supporté: {', '.join(product_mapping.keys())}")
        return

    try:
        api_product = product_mapping[os_name]
        url = f"https://endoflife.date/api/{api_product}.json"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        print(f"\n{'='*80}\n{os_name.upper()} - Versions et dates EOL\n{'='*80}")
        print(f"{'Version':<20} {'Support':<15} {'EOL':<15} {'Statut'}")
        print(f"{'-'*80}")

        for item in data[:15]:
            cycle, support, eol = item.get('cycle', 'N/A'), item.get('support', 'N/A'), item.get('eol', 'N/A')
            if isinstance(eol, bool):
                status = "✅ Actif" if eol else "❌ Terminé"
            else:
                try:
                    days = (datetime.strptime(str(eol), '%Y-%m-%d') - datetime.now()).days
                    status = "❌ Terminé" if days < 0 else (f"⚡ {days}j" if days < 365 else "✅ Actif")
                except:
                    status = "❓"
            print(f"{str(cycle):<20} {str(support):<15} {str(eol):<15} {status}")
        print(f"{'='*80}\n")
    except Exception as e:
        print(f"[!] Erreur: {e}")


def menu():
    """Menu principal"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("""
╔══════════════════════════════════════════════════════════╗
║         MODULE 3 : AUDIT D'OBSOLESCENCE RÉSEAU           ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    hosts = []

    while True:
        print("""
┌─────────────────────────────────────────────────────────┐
│  1. Scanner réseau                                      │
│  2. Importer CSV                                        │
│  3. Afficher hôtes                                      │
│  4. Lister versions d'un OS                             │
│  5. Générer rapport                                     │
│  0. Quitter                                             │
└─────────────────────────────────────────────────────────┘
        """)
        choice = input("Choix: ").strip()

        if choice == "1":
            network = input("Plage réseau (ex: 10.5.70.0/24): ").strip()
            if network:
                hosts = scan_network(network)
                show_hosts(hosts)
        elif choice == "2":
            csv_file = input("Fichier CSV: ").strip()
            if csv_file:
                hosts = import_csv(csv_file)
                show_hosts(hosts)
        elif choice == "3":
            show_hosts(hosts)
        elif choice == "4":
            print("OS: Windows, Windows Server, Ubuntu, Debian")
            list_all_versions(input("OS: ").strip())
        elif choice == "5":
            if hosts:
                generate_report(hosts, input("Nom rapport (défaut: rapport.html): ").strip() or "rapport.html")
            else:
                print("[!] Aucun hôte")
        elif choice == "0":
            print("\n[✓] Au revoir!\n")
            break


if __name__ == "__main__":
    menu()