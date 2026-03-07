import os
import sys
import subprocess
import getpass

SERVICE_NAME = "ollama-gateway"
SERVICE_FILE_PATH = f"/etc/systemd/system/{SERVICE_NAME}.service"

def get_service_content():
    # Détermine les chemins absolus
    working_dir = os.path.abspath(os.path.dirname(__file__))
    python_path = sys.executable
    user = getpass.getuser()

    return f"""[Unit]
Description=Ollama API Gateway with Quotas and Admin Panel
After=network.target ollama.service

[Service]
Type=simple
User={user}
WorkingDirectory={working_dir}
ExecStart={python_path} {working_dir}/run.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
"""

def install():
    if os.name == 'nt':
        print("❌ Erreur : systemd n'est disponible que sur Linux.")
        return

    print(f"--- Installation du service {SERVICE_NAME} ---")
    
    content = get_service_content()
    
    try:
        # Écriture du fichier service (nécessite sudo souvent, on va tenter d'utiliser sudo pour la copie)
        temp_file = "/tmp/ollama-gateway.service"
        with open(temp_file, "w") as f:
            f.write(content)
        
        print("Moving service file to /etc/systemd/system/...")
        subprocess.run(["sudo", "mv", temp_file, SERVICE_FILE_PATH], check=True)
        
        print("Reloading systemd...")
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        
        print("Enabling service...")
        subprocess.run(["sudo", "systemctl", "enable", SERVICE_NAME], check=True)
        
        print("Starting service...")
        subprocess.run(["sudo", "systemctl", "start", SERVICE_NAME], check=True)
        
        print(f"\n✅ Service installé et démarré !")
        print(f"Status : systemctl status {SERVICE_NAME}")
        print(f"Logs : journalctl -u {SERVICE_NAME} -f")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'installation : {e}")

def uninstall():
    if os.name == 'nt':
        print("❌ Erreur : systemd n'est disponible que sur Linux.")
        return

    print(f"--- Désinstallation du service {SERVICE_NAME} ---")
    
    try:
        print("Stopping service...")
        subprocess.run(["sudo", "systemctl", "stop", SERVICE_NAME], check=False)
        
        print("Disabling service...")
        subprocess.run(["sudo", "systemctl", "disable", SERVICE_NAME], check=False)
        
        print("Removing service file...")
        if os.path.exists(SERVICE_FILE_PATH) or True: # Force call sudo rm
            subprocess.run(["sudo", "rm", SERVICE_FILE_PATH], check=True)
        
        print("Reloading systemd...")
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        
        print(f"\n✅ Service {SERVICE_NAME} désinstallé avec succès.")
        
    except Exception as e:
        print(f"❌ Erreur lors de la désinstallation : {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage_service.py [install|uninstall]")
        sys.exit(1)
        
    command = sys.argv[1].lower()
    if command == "install":
        install()
    elif command == "uninstall":
        uninstall()
    else:
        print("Commande inconnue. Utilisez 'install' ou 'uninstall'.")
