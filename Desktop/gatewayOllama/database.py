import sqlite3
from datetime import datetime
from typing import Optional, List, Dict
import secrets

class Database:
    def __init__(self, db_path: str = "gateway.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Crée une connexion à la base de données."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialise la base de données avec les tables nécessaires."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table des utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                api_key TEXT UNIQUE NOT NULL,
                token_quota INTEGER DEFAULT 1000000,
                tokens_used INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table de l'historique des requêtes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                endpoint TEXT NOT NULL,
                tokens_consumed INTEGER DEFAULT 0,
                request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                model TEXT,
                status TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Indexation pour optimiser les requêtes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_logs_user_id ON request_logs(user_id)
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_api_key(self, username: str) -> str:
        """Génère une clé API unique pour un utilisateur."""
        prefix = f"sk-{username[:10]}-"
        random_part = secrets.token_urlsafe(16)
        return prefix + random_part
    
    def create_user(self, username: str, token_quota: int = 1000000) -> Dict:
        """Crée un nouveau utilisateur avec une clé API."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        api_key = self.generate_api_key(username)
        
        try:
            cursor.execute('''
                INSERT INTO users (username, api_key, token_quota)
                VALUES (?, ?, ?)
            ''', (username, api_key, token_quota))
            conn.commit()
            user_id = cursor.lastrowid
            
            return {
                "id": user_id,
                "username": username,
                "api_key": api_key,
                "token_quota": token_quota
            }
        except sqlite3.IntegrityError:
            conn.close()
            raise ValueError(f"L'utilisateur '{username}' existe déjà")
        finally:
            conn.close()
    
    def get_user_by_api_key(self, api_key: str) -> Optional[Dict]:
        """Récupère un utilisateur par sa clé API."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM users WHERE api_key = ? AND is_active = 1
        ''', (api_key,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Récupère un utilisateur par son ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_users(self) -> List[Dict]:
        """Récupère tous les utilisateurs."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, api_key, token_quota, tokens_used, 
                   is_active, created_at
            FROM users
            ORDER BY created_at DESC
        ''')
        
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return users
    
    def update_user_quota(self, user_id: int, new_quota: int) -> bool:
        """Met à jour le quota d'un utilisateur."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET token_quota = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_quota, user_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def toggle_user_status(self, user_id: int) -> bool:
        """Active/désactive un utilisateur."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET is_active = NOT is_active, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (user_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def delete_user(self, user_id: int) -> bool:
        """Supprime un utilisateur."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Supprime d'abord les logs associés
        cursor.execute('DELETE FROM request_logs WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def consume_tokens(self, api_key: str, tokens: int, endpoint: str, 
                      model: str = None, status: str = "success") -> bool:
        """
        Déduit des tokens du quota d'un utilisateur et enregistre la requête.
        Retourne True si le quota est suffisant, False sinon.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Récupère l'utilisateur
            cursor.execute('''
                SELECT id, tokens_used, token_quota 
                FROM users 
                WHERE api_key = ? AND is_active = 1
            ''', (api_key,))
            
            user = cursor.fetchone()
            if not user:
                return False
            
            user_id, tokens_used, token_quota = user
            
            # Vérifie si le quota est suffisant
            if tokens_used + tokens > token_quota:
                # Enregistre quand même la requête comme "quota_exceeded"
                cursor.execute('''
                    INSERT INTO request_logs 
                    (user_id, endpoint, tokens_consumed, model, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, endpoint, 0, model, "quota_exceeded"))
                conn.commit()
                conn.close()
                return False
            
            # Met à jour les tokens utilisés
            cursor.execute('''
                UPDATE users 
                SET tokens_used = tokens_used + ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (tokens, user_id))
            
            # Enregistre la requête
            cursor.execute('''
                INSERT INTO request_logs 
                (user_id, endpoint, tokens_consumed, model, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, endpoint, tokens, model, status))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Erreur lors de la consommation de tokens: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Récupère les statistiques d'un utilisateur."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Stats générales
        cursor.execute('''
            SELECT 
                COUNT(*) as total_requests,
                SUM(tokens_consumed) as total_tokens,
                MAX(request_time) as last_request
            FROM request_logs
            WHERE user_id = ?
        ''', (user_id,))
        
        stats = dict(cursor.fetchone())
        
        # Requêtes récentes
        cursor.execute('''
            SELECT endpoint, tokens_consumed, request_time, model, status
            FROM request_logs
            WHERE user_id = ?
            ORDER BY request_time DESC
            LIMIT 10
        ''', (user_id,))
        
        stats['recent_requests'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return stats
    
    def reset_user_tokens(self, user_id: int) -> bool:
        """Réinitialise le compteur de tokens d'un utilisateur."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET tokens_used = 0, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (user_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
