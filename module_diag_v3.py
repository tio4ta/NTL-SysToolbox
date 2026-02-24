import socket
import str
import datetime
import json
import pymysql
import os
import sys
import getpass
import paramiko
import winrm

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
    """Génère le JSON standardisé et lisible."""
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
    config = load_config()
    target_ip = config.get("DC_IP")
    dns_ok = check_port(target_ip, 53)
    ad_ok = check_port(target_ip, 389)
    status = "OK" if (dns_ok and ad_ok) else "ERROR"
    result = {"target_ip": target_ip, "dns_service": "UP" if dns_ok else "DOWN", "ad_service": "UP" if ad_ok else "DOWN"}
    return format_output("Check AD/DNS", status, result)

# --- 2. Tester Base SQL ---
def exec_check_sql():
    config = load_config()
    host = config.get("MYSQL_HOST")
    try:
        connection = pymysql.connect(host=host, user=config.get("MYSQL_USER"), password=config.get("MYSQL_PASSWORD"), database=config.get("MYSQL_DB"), connect_timeout=3)
        connection.ping(reconnect=False)
        connection.close()
        return format_output("Check SQL", "OK", {"host": host, "connection": "SUCCESS"})
    except Exception as e:
        return format_output("Check SQL", "ERROR", {"host": host, "connection": "FAILED", "error": str(e)})

# --- 3. Métriques Windows (via WinRM / PowerShell) ---
def exec_windows_metrics(ip, username, password):
    try:
        # Connexion WinRM (Port 5985 par défaut)
        session = winrm.Session(f'http://{ip}:5985/wsman', auth=(username, password), transport='ntlm')
        
        # Script PowerShell exécuté à distance pour formater directement en JSON
        ps_script = """
        $os = Get-CimInstance Win32_OperatingSystem
        $cpu = (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
        $ram = [math]::Round((($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize) * 100, 2)
        $disk = Get-CimInstance Win32_LogicalDisk | Where-Object DeviceID -eq 'C:'
        $disk_usage = [math]::Round((($disk.Size - $disk.FreeSpace) / $disk.Size) * 100, 2)
        $uptime = (Get-Date) - $os.LastBootUpTime
        $uptime_str = "{0} days, {1:hh\:mm\:ss}" -f $uptime.Days, $uptime
        
        @{
            os_version = "$($os.Caption) $($os.Version)"
            uptime = $uptime_str
            cpu_load = "$cpu%"
            ram_usage = "$ram%"
            disk_usage = "$disk_usage%"
        } | ConvertTo-Json
        """
        result = session.run_ps(ps_script)
        
        if result.status_code == 0:
            data = json.loads(result.std_out.decode('utf-8'))
            data["declared_target_ip"] = ip
            data["expected_os"] = "Windows"
            return format_output("Metrics Windows (WinRM)", "OK", data)
        else:
            return format_output("Metrics Windows (WinRM)", "ERROR", {"ip": ip, "error": result.std_err.decode('utf-8').strip()})
    except Exception as e:
        return format_output("Metrics Windows (WinRM)", "ERROR", {"ip": ip, "error": str(e)})

# --- 4. Métriques Ubuntu (via SSH) ---
def exec_ubuntu_metrics(ip, username, password):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # Accepte la clé SSH automatiquement
        client.connect(ip, username=username, password=password, timeout=5)

        # Commandes Bash exécutées à distance
        commands = {
            "os_version": "cat /etc/os-release | grep PRETTY_NAME | cut -d '\"' -f 2",
            "uptime": "uptime -p",
            "cpu_load": "top -bn1 | grep 'Cpu(s)' | awk '{print 100 - $8\"%\"}'",
            "ram_usage": "free | grep Mem | awk '{print int($3/$2 * 100.0)\"%\"}'",
            "disk_usage": "df -h / | awk 'NR==2 {print $5}'"
        }

        data = {"declared_target_ip": ip, "expected_os": "Ubuntu"}
        
        for key, cmd in commands.items():
            stdin, stdout, stderr = client.exec_command(cmd)
            data[key] = stdout.read().decode().strip()

        client.close()
        return format_output("Metrics Ubuntu (SSH)", "OK", data)
    except Exception as e:
        return format_output("Metrics Ubuntu (SSH)", "ERROR", {"ip": ip, "error": str(e)})

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
        print("3. OS UPTIME CPU RAM DISQUE Windows Server (via PowerShell)")
        print("4. OS UPTIME CPU RAM DISQUE Ubuntu (via SSH)")
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
            ip = input(">> IP du serveur Windows : ")
            user = input(">> Utilisateur admin : ")
            pwd = getpass.getpass(">> Mot de passe (masqué) : ")
            print(f"\n>> Connexion WinRM à {ip} en cours...")
            print(exec_windows_metrics(ip, user, pwd))
            input("\n[Entrée] pour continuer...")

        elif choice == "4":
            ip = input(">> IP du serveur Ubuntu : ")
            user = input(">> Utilisateur SSH : ")
            pwd = getpass.getpass(">> Mot de passe (masqué) : ")
            print(f"\n>> Connexion SSH à {ip} en cours...")
            print(exec_ubuntu_metrics(ip, user, pwd))
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
