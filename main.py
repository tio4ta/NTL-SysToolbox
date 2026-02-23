import sys
import os
import module_diag

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("==========================================")
    print("       NTL-SysToolbox - CLI 
    print("==========================================")

# --- Sous-menu Module 1 ---
def menu_module_1():
    while True:
        clear_screen()
        print_header()
        print("\n--- [MODULE 1] DIAGNOSTIC ---")
        print("1. Vérifier état des services AD / DNS")
        print("2. Tester base SQL")
        print("3. OS UPTIME CPU RAM DISQUE Windows Server")
        print("4. OS UPTIME CPU RAM DISQUE Ubuntu")
        print("R. Retour au menu principal")

        choice = input("\nVotre choix : ").strip().upper()

        if choice == "1":
            print("\n>> Exécution vérification AD/DNS...")
            print(module_diag.exec_check_ad_dns())
            input("\n[Entrée] pour continuer...")

        elif choice == "2":
            print("\n>> Exécution test MySQL...")
            print(module_diag.exec_check_mysql())
            input("\n[Entrée] pour continuer...")

        elif choice == "3":
            ip = input(">> Entrez l'IP du serveur Windows : ")
            print(f"\n>> Récupération métriques pour {ip} (Windows)...")
            # Note: psutil lit les infos de la machine locale
            print(module_diag.exec_system_metrics(ip, "Windows"))
            input("\n[Entrée] pour continuer...")

        elif choice == "4":
            ip = input(">> Entrez l'IP du serveur Ubuntu : ")
            print(f"\n>> Récupération métriques pour {ip} (Ubuntu)...")
            # Note: psutil lit les infos de la machine locale
            print(module_diag.exec_system_metrics(ip, "Ubuntu"))
            input("\n[Entrée] pour continuer...")

        elif choice == "R":
            break
        else:
            pass

# --- Menu Principal ---
def main_menu():
    while True:
        clear_screen()
        print_header()
        print("\nSÉLECTION DU MODULE :")
        print("1. [Module 1] Diagnostic")
        print("2. [Module 2] Sauvegarde WMS")
        print("3. [Module 3] Audit d'Obsolescence")
        print("Q. Quitter")
       
        choice = input("\nVotre choix : ").strip().upper()
       
        if choice == "1":
            menu_module_1()
        elif choice == "2":
            print("\nModule en construction...")
            input("[Entrée] pour continuer")
        elif choice == "3":
            print("\nModule en construction...")
            input("[Entrée] pour continuer")
        elif choice == "Q":
            print("Au revoir !")
            sys.exit(0)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        sys.exit(0)