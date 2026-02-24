import paramiko
import os
import json
import platform
import pymysql
import pandas as pd
from pathlib import Path
from datetime import datetime

class WMSManager:
    def __init__(self):
        # Localisation du dossier racine
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(self.root_dir, 'Configuration.json')
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Configuration du dossier de sauvegarde SQL (Défini dans le JSON)
        local_rel = self.config['paths']['local_backup_dir'].strip("./").strip("/")
        self.local_backup_folder = os.path.join(self.root_dir, local_rel)
        
        # Dossier de sortie CSV portable (Windows/Linux)
        self.output_dir_csv = Path.home() / "Documents" / "export_wms" if platform.system() == "Windows" else Path.home() / "export_wms"
        
        # Création des dossiers si nécessaires
        for folder in [self.local_backup_folder, self.output_dir_csv]:
            if not os.path.exists(folder):
                os.makedirs(folder)

        self.date = datetime.now().strftime("%Y%m%d_%H%M")
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect_ssh(self):
        ssh_conf = self.config['ssh']
        self.client.connect(hostname=ssh_conf['host'], username=ssh_conf['user'], password=ssh_conf['pass'])

    def run_backup(self):
        """ Génère un dump des tables cibles et le rapatrie """
        try:
            self.connect_ssh()
            db = self.config['db']
            tables = "expedition reception"
            filename = f"ntl_wms_tables_{self.date}.sql"
            remote_temp_path = f"/tmp/{filename}"

            print(f"--- [BACKUP SQL] Dump des tables {tables} ---")
            cmd = f"mysqldump -u {db['user']} -p'{db['pass']}' {db['name']} {tables} > {remote_temp_path}"
            self.client.exec_command(cmd)

            sftp = self.client.open_sftp()
            sftp.get(remote_temp_path, os.path.join(self.local_backup_folder, filename))
            sftp.close()

            self.client.exec_command(f"rm {remote_temp_path}")
            print(f"Sauvegarde SQL réussie : {filename}")
        except Exception as e:
            print(f"Erreur Backup : {e}")
        finally:
            self.client.close()

    def run_export_csv(self):
        """ Exporte les tables expedition et reception en fichiers CSV localement """
        print(f"--- [EXPORT CSV] Connexion à la base de données ---")
        db_conf = self.config['db']
        host = self.config['ssh']['host']
        tables = ["expedition", "reception"]
        
        try:
            # Connexion via pymysql
            connection = pymysql.connect(
                host=host,
                user=db_conf['user'],
                password=db_conf['pass'],
                database=db_conf['name']
            )
            
            for table in tables:
                query = f"SELECT * FROM {table}"
                # Utilisation de pandas pour lire le SQL et convertir en CSV
                df = pd.read_sql(query, connection)
                
                csv_filename = f"{table}_{self.date}.csv"
                csv_path = self.output_dir_csv / csv_filename
                
                df.to_csv(csv_path, index=False, encoding='utf-8-sig', sep=';')
                print(f"Table '{table}' exportée : {csv_path}")
                
            connection.close()
        except Exception as e:
            print(f"Erreur Export CSV : {e}")

    def run_restore(self):
        """ Restauration SQL (ton code précédent) """
        try:
            files = [f for f in os.listdir(self.local_backup_folder) if f.endswith('.sql')]
            if not files:
                print("Aucun fichier de sauvegarde trouvé.")
                return

            print("\n--- [RESTAURATION] Choisissez un fichier ---")
            for i, f in enumerate(files):
                print(f"{i + 1}. {f}")
            
            choice = int(input("\nNuméro du fichier : ")) - 1
            selected_file = files[choice]
            local_file_path = os.path.join(self.local_backup_folder, selected_file)
            remote_temp_path = f"/tmp/{selected_file}"

            self.connect_ssh()
            print(f"Envoi de {selected_file} vers Debian...")
            sftp = self.client.open_sftp()
            sftp.put(local_file_path, remote_temp_path)
            sftp.close()

            db = self.config['db']
            restore_cmd = f"mysql -u {db['user']} -p'{db['pass']}' {db['name']} < {remote_temp_path}"
            self.client.exec_command(restore_cmd)
            
            print(f"Restauration de '{selected_file}' terminée.")
            self.client.exec_command(f"rm {remote_temp_path}")

        except Exception as e:
            print(f"Erreur Restauration : {e}")
        finally:
            self.client.close()

if __name__ == "__main__":
    manager = WMSManager()
    print("==============================")
    print("      NTL WMS MANAGER")
    print("==============================")
    print("1. Lancer un Backup (SQL)")
    print("2. Restaurer une Sauvegarde (SQL)")
    print("3. Exporter les données en CSV")
    
    mode = input("\nVotre choix : ")
    
    if mode == "1":
        manager.run_backup()
    elif mode == "2":
        manager.run_restore()
    elif mode == "3":
        manager.run_export_csv()
    else:
        print("Choix invalide.")
