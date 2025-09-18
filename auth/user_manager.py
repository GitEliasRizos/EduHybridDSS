import sqlite3
import hashlib
import os
from typing import Optional, List, Dict, Any
import numpy as np
import json

class UserManager:
    """Manages user authentication and group decision making data"""
    
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the user database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # AHP comparisons table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ahp_comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                session_id TEXT NOT NULL,
                criteria_names TEXT NOT NULL,
                comparison_matrix TEXT NOT NULL,
                weights TEXT NOT NULL,
                consistency_ratio REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users (username)
            )
        ''')
        
        # TOPSIS weights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topsis_weights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                session_id TEXT NOT NULL,
                criteria_names TEXT NOT NULL,
                weights TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users (username)
            )
        ''')
        
        # Group sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                problem_name TEXT NOT NULL,
                criteria_names TEXT NOT NULL,
                created_by TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (username)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, password: str, role: str = 'user') -> bool:
        """Create a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self._hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role)
            )
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def verify_user(self, username: str, password: str) -> bool:
        """Verify user credentials"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self._hash_password(password)
            cursor.execute(
                "SELECT password_hash FROM users WHERE username = ?",
                (username,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            return result is not None and result[0] == password_hash
        except Exception as e:
            print(f"Error verifying user: {e}")
            return False
    
    def user_exists(self, username: str) -> bool:
        """Check if user exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
        except Exception as e:
            print(f"Error checking user existence: {e}")
            return False
    
    def get_user_role(self, username: str) -> Optional[str]:
        """Get user role"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting user role: {e}")
            return None
    
    def create_group_session(self, session_id: str, problem_name: str, 
                           criteria_names: List[str], created_by: str) -> bool:
        """Create a new group decision making session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO group_sessions (session_id, problem_name, criteria_names, created_by) VALUES (?, ?, ?, ?)",
                (session_id, problem_name, json.dumps(criteria_names), created_by)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating group session: {e}")
            return False
    
    def save_ahp_comparison(self, username: str, session_id: str, 
                          criteria_names: List[str], comparison_matrix: np.ndarray,
                          weights: np.ndarray, consistency_ratio: float) -> bool:
        """Save user's AHP comparison"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Remove existing comparison for this user and session
            cursor.execute(
                "DELETE FROM ahp_comparisons WHERE username = ? AND session_id = ?",
                (username, session_id)
            )
            
            cursor.execute(
                """INSERT INTO ahp_comparisons 
                   (username, session_id, criteria_names, comparison_matrix, weights, consistency_ratio) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (username, session_id, json.dumps(criteria_names), 
                 json.dumps(comparison_matrix.tolist()), json.dumps(weights.tolist()), 
                 consistency_ratio)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving AHP comparison: {e}")
            return False
    
    def save_topsis_weights(self, username: str, session_id: str,
                          criteria_names: List[str], weights: np.ndarray) -> bool:
        """Save user's TOPSIS weights"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Remove existing weights for this user and session
            cursor.execute(
                "DELETE FROM topsis_weights WHERE username = ? AND session_id = ?",
                (username, session_id)
            )
            
            cursor.execute(
                """INSERT INTO topsis_weights 
                   (username, session_id, criteria_names, weights) 
                   VALUES (?, ?, ?, ?)""",
                (username, session_id, json.dumps(criteria_names), 
                 json.dumps(weights.tolist()))
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving TOPSIS weights: {e}")
            return False
    
    def get_group_ahp_data(self, session_id: str) -> Dict[str, Any]:
        """Get all AHP comparisons for a group session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT username, criteria_names, comparison_matrix, weights, consistency_ratio 
                   FROM ahp_comparisons WHERE session_id = ?""",
                (session_id,)
            )
            
            results = cursor.fetchall()
            conn.close()
            
            group_data = {
                'users': [],
                'matrices': [],
                'weights': [],
                'consistency_ratios': [],
                'criteria_names': None
            }
            
            for row in results:
                username, criteria_names, matrix_json, weights_json, cr = row
                group_data['users'].append(username)
                group_data['matrices'].append(np.array(json.loads(matrix_json)))
                group_data['weights'].append(np.array(json.loads(weights_json)))
                group_data['consistency_ratios'].append(cr)
                
                if group_data['criteria_names'] is None:
                    group_data['criteria_names'] = json.loads(criteria_names)
            
            return group_data
        except Exception as e:
            print(f"Error getting group AHP data: {e}")
            return {}
    
    def get_group_topsis_data(self, session_id: str) -> Dict[str, Any]:
        """Get all TOPSIS weights for a group session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT username, criteria_names, weights 
                   FROM topsis_weights WHERE session_id = ?""",
                (session_id,)
            )
            
            results = cursor.fetchall()
            conn.close()
            
            group_data = {
                'users': [],
                'weights': [],
                'criteria_names': None
            }
            
            for row in results:
                username, criteria_names, weights_json = row
                group_data['users'].append(username)
                group_data['weights'].append(np.array(json.loads(weights_json)))
                
                if group_data['criteria_names'] is None:
                    group_data['criteria_names'] = json.loads(criteria_names)
            
            return group_data
        except Exception as e:
            print(f"Error getting group TOPSIS data: {e}")
            return {}
    
    def aggregate_ahp_matrices(self, matrices: List[np.ndarray]) -> np.ndarray:
        """Aggregate multiple AHP comparison matrices using geometric mean"""
        if not matrices:
            return np.array([])
        
        # Initialize with first matrix
        result = matrices[0].copy()
        
        # Multiply all matrices element-wise
        for matrix in matrices[1:]:
            result = result * matrix
        
        # Take nth root where n is number of matrices
        n = len(matrices)
        result = np.power(result, 1.0 / n)
        
        return result
    
    def aggregate_topsis_weights(self, weights_list: List[np.ndarray]) -> np.ndarray:
        """Aggregate multiple TOPSIS weight vectors using arithmetic mean"""
        if not weights_list:
            return np.array([])
        
        # Stack weights and compute mean
        weights_matrix = np.vstack(weights_list)
        aggregated = np.mean(weights_matrix, axis=0)
        
        # Normalize to sum to 1
        return aggregated / np.sum(aggregated)
    
    def get_all_users(self) -> List[Dict[str, str]]:
        """Get all users with their roles"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT username, role, created_at FROM users")
            results = cursor.fetchall()
            conn.close()
            
            return [{'username': row[0], 'role': row[1], 'created_at': row[2]} 
                   for row in results]
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def get_group_sessions(self) -> List[Dict[str, Any]]:
        """Get all group sessions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT session_id, problem_name, criteria_names, created_by, status, created_at FROM group_sessions"
            )
            results = cursor.fetchall()
            conn.close()
            
            sessions = []
            for row in results:
                sessions.append({
                    'session_id': row[0],
                    'problem_name': row[1],
                    'criteria_names': json.loads(row[2]),
                    'created_by': row[3],
                    'status': row[4],
                    'created_at': row[5]
                })
            
            return sessions
        except Exception as e:
            print(f"Error getting group sessions: {e}")
            return []