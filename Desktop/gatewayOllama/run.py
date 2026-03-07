import subprocess
import os
import time
import sys

def run_services():
    print("--- Démarrage de Ollama Gateway Suite ---")
    
    # Installation des dépendances si nécessaire
    # subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # Lancement de la Gateway (FastAPI) sur le port 8000
    gateway_process = subprocess.Popen([sys.executable, "gateway.py"])
    print("✅ Gateway démarrée sur http://localhost:8000")

    # Lancement du Panel Admin (Flask) sur le port 5000
    admin_process = subprocess.Popen([sys.executable, "admin_panel.py"])
    print("✅ Panel Admin démarré sur http://localhost:5000")

    print("\nUtilisez Ctrl+C pour arrêter les deux services.")
    
    try:
        while True:
            time.sleep(1)
            # Vérifier si les processus sont toujours vivants
            if gateway_process.poll() is not None:
                print("L'application Gateway s'est arrêtée.")
                break
            if admin_process.poll() is not None:
                print("L'application Admin s'est arrêtée.")
                break
    except KeyboardInterrupt:
        print("\nArrêt des services...")
    finally:
        gateway_process.terminate()
        admin_process.terminate()
        print("Services arrêtés.")

if __name__ == "__main__":
    run_services()
