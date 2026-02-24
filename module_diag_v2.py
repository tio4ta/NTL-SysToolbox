import platform
import psutil
import socket
import datetime
import json
import pymysql
import os
import sys

# --- Gestion de la Config ---
def load_config():
    """Charge la configuration depuis config.json et surcharge avec les variables d'environnement."""
    config = {}
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            config = json.load(f)
    
    return {
        "DC_IP": os.environ.get("NTL_DC_IP", config.get("DC_IP", "192.168.10.10")),
        "MYSQL_HOST": os.environ.get("NTL_MYSQL_HOST", config.get("MYSQL_HOST", "192.168.10.21")),
        "MYSQL_USER": os.environ.get("NTL_MYSQL_USER", config.get("MYSQL_USER", "root")),
        "MYSQL_PASSWORD": os.environ.get("NTL_MYSQL_PASSWORD", config.get("MYSQL_PASSWORD", "")),
        "MYSQL_DB": os.environ.get("NTL_MYSQL_DB", config.get("MYSQL_DB", "wms_db"))
    }

# --- Fonctions Utilitaires ---
def get_timestamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def format_output(module_name, status, data):
    """Génère le JSON standardisé et lisible[cite: 92, 117]."""
    return json.dumps({
        "timestamp": get_timestamp(),
        "module": module_name,
        "global_status": status,
        "data": data
    }, indent=4)

def check_port(ip, port, timeout=2):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((ip, port))
        return True
    except:
        return False

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# --- 1. Vérifier AD / DNS ---
def exec_check_ad_dns():
    """Vérifier l'état des services AD / DNS sur les contrôleurs de domaine[cite: 96]."""
    config = load_config()
    target_ip = config.get("DC_IP")
    
    dns_ok = check_port(target_ip, 53)
    ad_ok = check_port(target_ip, 389)
    status = "OK" if (dns_ok and ad_ok) else "ERROR"
    
    result = {
        "target_ip": target_ip,
        "dns_service": "UP" if dns_ok else "DOWN",
        "ad_service": "UP" if ad_ok else "DOWN"
    }
    return format_output("Check AD/DNS", status, result)

# --- 2. Tester Base SQL ---
def exec_check_sql():
    """Tester le bon fonctionnement de la base de données MYSQL/MariaDB[cite: 97]."""
    config = load_config()
    host = config.get("MYSQL_HOST")
    
    try:
        connection = pymysql.connect(
            host=host,
            user=config.get("MYSQL_USER"),
            password=config.get("MYSQL_PASSWORD"),
            database=config.get("MYSQL_DB"),
            connect_timeout=3
        )
        connection.ping(reconnect=False)
        connection.close()
        return format_output("Check SQL", "OK", {"host": host, "connection": "SUCCESS"})
    except Exception as e:
        return format_output("Check SQL", "ERROR", {"host": host, "connection": "FAILED", "error": str(e)})

# --- 3 & 4. Métriques Système (Windows/Ubuntu) ---
def exec_system_metrics(target_ip, os_type_expected):
    """Vérifier la version d'OS, l'uptime, l'utilisation CPU/RAM/Disques[cite: 98, 99]."""
    real_os = platform.system()
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = str(datetime.datetime.now() - boot_time).split('.')[0]
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('C:\\' if real_os == "Windows" else '/').percent

    status = "OK"
    warning = None
    if os_type_expected == "Windows" and real_os != "Windows":
        status = "WARNING"
        warning = "Script exécuté sur Linux mais menu Windows sélectionné"
    elif os_type_expected == "Ubuntu" and real_os == "Windows":
        status = "WARNING"
        warning = "Script exécuté sur Windows mais menu Ubuntu sélectionné"

    data = {
        "declared_target_ip": target_ip,
        "expected_os": os_type_expected,
        "detected_os": f"{real_os} {platform.release()}",
        "uptime": uptime,
        "cpu_load": f"{cpu}%",
        "ram_usage": f"{ram}%",
        "disk_usage": f"{disk}%"
    }
    
    if warning:
        data["warning"] = warning

    return format_output(f"Metrics {os_type_expected}", status, data)

# --- MENU PRINCIPAL ---
def main_menu():
    while True:
        clear_screen()
        print("==========================================")
        print("       NTL-SysToolbox - Module 1")
        print("==========================================")
        print("\nMENU DIAGNOSTIC :")
        print("1. Vérifier état des services AD / DNS")
        print("2. Tester base SQL (MySQL / MariaDB)")
        print("3. OS UPTIME CPU RAM DISQUE Windows Server")
        print("4. OS UPTIME CPU RAM DISQUE Ubuntu")
        print("Q. Quitter")

        choice = input("\nVotre choix : ").strip().upper()

        if choice == "1":
            print("\n>> Exécution vérification AD/DNS...")
            print(exec_check_ad_dns())
            input("\n[Entrée] pour continuer...")

        elif choice == "2":
            print("\n>> Exécution test SQL...")
            print(exec_check_sql())
            input("\n[Entrée] pour continuer...")

        elif choice == "3":
            ip = input(">> Entrez l'IP du serveur Windows : ")
            print(f"\n>> Récupération métriques pour {ip} (Windows)...")
            print(exec_system_metrics(ip, "Windows"))
            input("\n[Entrée] pour continuer...")

        elif choice == "4":
            ip = input(">> Entrez l'IP du serveur Ubuntu : ")
            print(f"\n>> Récupération métriques pour {ip} (Ubuntu)...")
            print(exec_system_metrics(ip, "Ubuntu"))
            input("\n[Entrée] pour continuer...")

        elif choice == "Q":
            print("Fermeture de l'outil. Au revoir !")
            sys.exit(0)
        else:
            print("Choix invalide.")
            input("Appuyez sur Entrée pour réessayer...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nInterruption détectée. Fermeture...")
        sys.exit(0)
