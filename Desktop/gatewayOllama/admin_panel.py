from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from functools import wraps
from database import Database
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Mkasholsen31@')

db = Database()

def login_required(f):
    """Décorateur pour protéger les routes admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Identifiants incorrects')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Déconnexion."""
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Dashboard principal."""
    users = db.get_all_users()
    
    # Calculer les statistiques globales
    total_users = len(users)
    active_users = sum(1 for u in users if u['is_active'])
    total_tokens_used = sum(u['tokens_used'] for u in users)
    total_quota = sum(u['token_quota'] for u in users)
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'total_tokens_used': total_tokens_used,
        'total_quota': total_quota
    }
    
    return render_template('dashboard.html', users=users, stats=stats)

@app.route('/user/<int:user_id>')
@login_required
def user_detail(user_id):
    """Détails d'un utilisateur."""
    user = db.get_user_by_id(user_id)
    if not user:
        return "Utilisateur non trouvé", 404
    
    stats = db.get_user_stats(user_id)
    return render_template('user_detail.html', user=user, stats=stats)

@app.route('/api/users', methods=['POST'])
@login_required
def create_user():
    """Crée un nouveau utilisateur."""
    data = request.get_json()
    username = data.get('username')
    token_quota = int(data.get('token_quota', 1000000))
    
    if not username:
        return jsonify({'error': 'Le nom d\'utilisateur est requis'}), 400
    
    try:
        user = db.create_user(username, token_quota)
        return jsonify(user), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/users/<int:user_id>/quota', methods=['PUT'])
@login_required
def update_quota(user_id):
    """Met à jour le quota d'un utilisateur."""
    data = request.get_json()
    new_quota = int(data.get('quota'))
    
    if db.update_user_quota(user_id, new_quota):
        return jsonify({'success': True})
    return jsonify({'error': 'Utilisateur non trouvé'}), 404

@app.route('/api/users/<int:user_id>/toggle', methods=['POST'])
@login_required
def toggle_user(user_id):
    """Active/désactive un utilisateur."""
    if db.toggle_user_status(user_id):
        return jsonify({'success': True})
    return jsonify({'error': 'Utilisateur non trouvé'}), 404

@app.route('/api/users/<int:user_id>/reset', methods=['POST'])
@login_required
def reset_tokens(user_id):
    """Réinitialise les tokens consommés d'un utilisateur."""
    if db.reset_user_tokens(user_id):
        return jsonify({'success': True})
    return jsonify({'error': 'Utilisateur non trouvé'}), 404

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    """Supprime un utilisateur."""
    if db.delete_user(user_id):
        return jsonify({'success': True})
    return jsonify({'error': 'Utilisateur non trouvé'}), 404

if __name__ == '__main__':
    # S'assure que les répertoires nécessaires existent
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("Panel Admin démarré sur http://localhost:5000")
    print(f"Identifiants par défaut: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
    app.run(host='0.0.0.0', port=5000, debug=True)
