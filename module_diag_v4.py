import socket
import datetime
import json
import pymysql
import os
import sys
import getpass
import paramiko
import winrm

# --- Gestion de la Config  ---
def load_config():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(root_dir, "Configuration.json")
    
    if not os.path.exists(config_path):
        print(f"CRITICAL ERROR: {config_path} introuvable.")
        sys.exit(1)
        
    with open(config_path, "r", encoding='utf-8') as f:
        return json.load(f)

# --- Fonctions Utilitaires ---
def get_timestamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def format_output(module_name, status, data):
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

def ask_target_ip(default_ip, label):
    print(f"\n--- Choix de la cible {label} ---")
    print(f"1. Utiliser l'IP par défaut ({default_ip})")
    print(f"2. Saisir une adresse IP manuellement")
    choice = input("Votre choix : ").strip()
    
    if choice == "2":
        return input("Saisissez l'adresse IP de la cible : ").strip()
    return default_ip

# --- 1. Vérifier AD / DNS (Full Auto via JSON) ---
def exec_check_ad_dns(config):
    target_ip = config["dc"]["host"]
    dns_ok = check_port(target_ip, 53)
    ad_ok = check_port(target_ip, 389)
    status = "OK" if (dns_ok and ad_ok) else "ERROR"
    result = {
        "target_ip": target_ip, 
        "services": {"DNS (53)": "UP" if dns_ok else "DOWN", "LDAP (389)": "UP" if ad_ok else "DOWN"}
    }
    return format_output("Check AD/DNS", status, result)

# --- 2. Tester Base SQL (Full Auto via JSON) ---
def exec_check_sql(config):
    db_conf = config["db"]
    target_host = config["ssh"]["host"]
    
    try:
        connection = pymysql.connect(
            host=target_host, 
            user=db_conf["user"], 
            password=db_conf["pass"], 
            database=db_conf["name"], 
            connect_timeout=3
        )
        connection.ping(reconnect=False)
        connection.close()
        return format_output("Check SQL", "OK", {"host": target_host, "status": "CONNECTED"})
    except Exception as e:
        return format_output("Check SQL", "ERROR", {"host": target_host, "error": str(e)})

# --- 3. Métriques Windows ---
def exec_windows_metrics(ip, username, password):
    try:
        session = winrm.Session(f'http://{ip}:5985/wsman', auth=(username, password), transport='ntlm')
        ps_script = r"""
        $os = Get-CimInstance Win32_OperatingSystem
        $cpu = (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
        $ram = [math]::Round((($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize) * 100, 2)
        $disk = Get-CimInstance Win32_LogicalDisk | Where-Object DeviceID -eq 'C:'
        $disk_usage = [math]::Round((($disk.Size - $disk.FreeSpace) / $disk.Size) * 100, 2)
        @{ os = $os.Caption; cpu = "$cpu%"; ram = "$ram%"; disk = "$disk_usage%" } | ConvertTo-Json
        """
        result = session.run_ps(ps_script)
        if result.status_code == 0:
            return format_output("Metrics Windows", "OK", json.loads(result.std_out.decode('utf-8')))
        return format_output("Metrics Windows", "ERROR", {"error": result.std_err.decode().strip()})
    except Exception as e:
        return format_output("Metrics Windows", "ERROR", {"error": str(e)})

# --- 4. Métriques Ubuntu ---
def exec_ubuntu_metrics(ip, username, password):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        client.connect(ip, username=username, password=password, timeout=5)

        cmds = {
            "os": "cat /etc/os-release | grep PRETTY_NAME | cut -d '\"' -f 2",
            "cpu": "top -bn1 | grep 'Cpu(s)' | awk '{print 100 - $8\"%\"}'",
            "ram": "free | grep Mem | awk '{print int($3/$2 * 100.0)\"%\"}'",
            "disk": "df -h / | awk 'NR==2 {print $5}'"
        }
        data = {"target_ip": ip}
        for key, cmd in cmds.items():
            stdin, stdout, stderr = client.exec_command(cmd)
            data[key] = stdout.read().decode().strip()
        client.close()
        return format_output("Metrics Ubuntu", "OK", data)
    except Exception as e:
        return format_output("Metrics Ubuntu", "ERROR", {"error": str(e)})

# --- MENU PRINCIPAL ---
def main_menu():
    config = load_config()
    while True:
        clear_screen()
        print("===================================")
        print("       NTL-SysToolbox")
        print("===================================")
        print(f"IP Debian (DB) : {config['ssh']['host']}")
        print(f"IP Windows (DC) : {config['dc']['host']}")
        print("------------------------------------------")
        print("1. État AD / DNS (Auto)")
        print("2. État Base SQL (Auto)")
        print("3. Santé Windows Server (Choix IP + Saisie ID)")
        print("4. Santé Ubuntu Server (Choix IP + Saisie ID)")
        print("Q. Quitter")

        choice = input("\nVotre choix : ").strip().upper()

        if choice == "1":
            print(exec_check_ad_dns(config))
        elif choice == "2":
            print(exec_check_sql(config))
        elif choice == "3":
            # Choix de l'IP Windows
            ip = ask_target_ip(config["dc"]["host"], "Windows (DC)")
            print(f"\n>> Cible finale : {ip}")
            user = input("Utilisateur Admin : ")
            pwd = getpass.getpass("Mot de passe (masqué) : ")
            print(exec_windows_metrics(ip, user, pwd))
            
        elif choice == "4":
            # Choix de l'IP Ubuntu
            ip = ask_target_ip(config["ssh"]["host"], "Ubuntu (DB)")
            print(f"\n>> Cible finale : {ip}")
            user = input("Utilisateur SSH : ")
            pwd = getpass.getpass("Mot de passe (masqué) : ")
            print(exec_ubuntu_metrics(ip, user, pwd))
            
        elif choice == "Q":
            break
        
        input("\n[Entrée] pour continuer...")

if __name__ == "__main__":
    main_menu()
