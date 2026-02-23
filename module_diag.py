import platform
import psutil
import socket
import datetime
import json
import pymysql
import os

# --- Gestion de la Config ---
def load_config():
    config = {}
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            config = json.load(f)
    return config

# --- Fonctions Utilitaires ---
def get_timestamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def format_output(module_name, status, data):
    """Génère le JSON standardisé"""
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

# --- 1. Vérifier AD / DNS ---
def exec_check_ad_dns():
    config = load_config()
    target_ip = config.get("DC_IP", "192.168.10.10")
   
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
def exec_check_mysql():
    config = load_config()
    host = config.get("MYSQL_HOST", "127.0.0.1")
   
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
        return format_output("Check MySQL", "OK", {"host": host, "connection": "SUCCESS"})
    except Exception as e:
        return format_output("Check MySQL", "ERROR", {"host": host, "connection": "FAILED", "error": str(e)})

# --- 3 & 4. Métriques Système (Windows/Ubuntu) ---
def exec_system_metrics(target_ip, os_type_expected):
    """
    Note : Psutil récupère les infos de la machine locale où le script est lancé.
    Dans une vraie supervision sans agent, on utiliserait WMI ou SSH via l'IP.
    Ici, on simule l'association de l'IP saisie aux métriques locales.
    """
   
    # Récupération des infos locales
    real_os = platform.system()
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = str(datetime.datetime.now() - boot_time).split('.')[0]
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('C:\\' if real_os == "Windows" else '/').percent

    # Vérification de cohérence (optionnel)
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