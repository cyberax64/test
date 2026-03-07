# 🦙 Ollama API Gateway

Un **reverse proxy intelligent** pour Ollama avec gestion de quotas de tokens, clés API et panel d'administration web.

---

## 🚀 Présentation

**Ollama API Gateway** permet d'exposer votre instance Ollama locale à plusieurs utilisateurs tout en contrôlant leur consommation de tokens. Chaque utilisateur reçoit une clé API unique et un quota configurable. Toutes les requêtes sont journalisées dans une base SQLite.

```
Client (avec clé API)
       │
       ▼
┌─────────────────────┐        ┌──────────────────┐
│   API Gateway       │──────▶│  Ollama (local)  │
│   FastAPI :8000     │        │  :11434          │
└─────────────────────┘        └──────────────────┘
       │
       ▼
┌─────────────────────┐
│  Panel Admin        │
│  Flask :5000        │
└─────────────────────┘
```

---

## ✨ Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| 🔑 **Clés API** | Génération automatique de clés `Bearer` par utilisateur |
| 📊 **Quotas de tokens** | Limite configurable par utilisateur (défaut : 1M tokens) |
| 📜 **Journalisation** | Historique complet des requêtes (endpoint, modèle, tokens) |
| 🔒 **Blocage automatique** | Requêtes refusées si quota dépassé (HTTP 402) |
| 🌐 **Proxy transparent** | Compatible avec toutes les routes Ollama (natif & OpenAI compat) |
| 🖥️ **Panel Admin** | Interface web pour gérer les utilisateurs et visualiser les stats |
| ⚙️ **Service Linux** | Installation en tant que service systemd optionnelle |

---

## 📋 Prérequis

- Python **3.9+**
- [Ollama](https://ollama.com/) installé et en cours d'exécution sur `http://127.0.0.1:11434`

---

## 🛠️ Installation

### 1. Cloner le projet

```bash
git clone https://github.com/cyberax64/test.git
cd test
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Lancer les services

```bash
python run.py
```

Cela démarre simultanément :
- ✅ **API Gateway** → `http://localhost:8000`
- ✅ **Panel Admin** → `http://localhost:5000`

---

## 🔌 Utilisation de l'API

L'API Gateway est **entièrement compatible** avec l'API Ollama. Il suffit de pointer vers `http://localhost:8000` et d'ajouter votre clé API dans le header `Authorization`.

### Exemple — Chat (format Ollama natif)

```bash
curl http://localhost:8000/api/chat \
  -H "Authorization: Bearer sk-monuser-XXXXXXXXXXXX" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3",
    "messages": [{"role": "user", "content": "Bonjour !"}]
  }'
```

### Exemple — Chat (format OpenAI compatible)

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer sk-monuser-XXXXXXXXXXXX" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3",
    "messages": [{"role": "user", "content": "Bonjour !"}]
  }'
```

### Codes d'erreur HTTP

| Code | Signification |
|---|---|
| `401` | Header `Authorization` manquant ou malformé |
| `403` | Clé API invalide ou utilisateur désactivé |
| `402` | Quota de tokens dépassé |
| `502` | Ollama injoignable |

---

## 🖥️ Panel d'Administration

Accédez au panel sur `http://localhost:5000`.

**Identifiants par défaut :**
- Utilisateur : `admin`
- Mot de passe : défini via la variable d'environnement `ADMIN_PASSWORD`

> ⚠️ **Sécurité** : Changez impérativement les identifiants via les variables d'environnement en production !

### Fonctionnalités du panel

- 📋 **Dashboard** : Vue globale (nb utilisateurs, tokens consommés, quota total)
- 👤 **Détail utilisateur** : Historique des 10 dernières requêtes, stats de consommation
- ➕ **Créer un utilisateur** : Génération automatique de la clé API
- ✏️ **Modifier le quota** : Mise à jour du quota de tokens en temps réel
- 🔄 **Activer/Désactiver** : Toggle du statut d'un compte
- 🔁 **Réinitialiser les tokens** : Remise à zéro du compteur
- 🗑️ **Supprimer** : Suppression d'un utilisateur et de ses logs

---

## 🗂️ Structure du projet

```
gatewayOllama/
├── gateway.py          # API Gateway FastAPI (proxy + comptage tokens)
├── admin_panel.py      # Panel d'administration Flask
├── database.py         # Gestion SQLite (utilisateurs, logs, quotas)
├── run.py              # Lanceur multi-processus (gateway + admin)
├── manage_service.py   # Gestion du service systemd (Linux)
├── requirements.txt    # Dépendances Python
├── static/
│   ├── style.css       # Styles du panel admin
│   └── script.js       # Scripts frontend du panel admin
└── templates/
    ├── login.html      # Page de connexion
    ├── dashboard.html  # Tableau de bord principal
    └── user_detail.html # Détail d'un utilisateur
```

---

## ⚙️ Configuration

Les paramètres sont configurables via des **variables d'environnement** :

| Variable | Défaut | Description |
|---|---|---|
| `ADMIN_USERNAME` | `admin` | Login du panel admin |
| `ADMIN_PASSWORD` | `Mkasholsen31@` | Mot de passe du panel admin |
| `SECRET_KEY` | `dev-secret-key-...` | Clé secrète des sessions Flask |

La configuration d'Ollama (URL cible) se trouve dans `gateway.py` :

```python
OLLAMA_URL = "http://127.0.0.1:11434"
```

---

## 🐧 Installation comme service Linux (systemd)

Pour que la gateway démarre automatiquement au boot :

```bash
# Installer le service
python manage_service.py install

# Voir les logs en temps réel
journalctl -u ollama-gateway -f

# Désinstaller
python manage_service.py uninstall
```

---

## 📦 Dépendances

| Package | Rôle |
|---|---|
| `fastapi` | Framework de l'API Gateway |
| `uvicorn` | Serveur ASGI pour FastAPI |
| `httpx` | Client HTTP asynchrone (proxy vers Ollama) |
| `flask` | Framework du panel d'administration |
| `jinja2` | Moteur de templates HTML |
| `python-dotenv` | Chargement des variables d'environnement |

---

## 📝 Licence

Projet libre — à utiliser et modifier selon vos besoins.
