import sqlite3
import hashlib
import os
from typing import Optional, List, Dict, Any
import numpy as np
import json

class UserManager:
    """Manages user authentication and group decision making data"""
    
    ADMIN_USERNAME = "iiooooiooi"
    ADMIN_PASSWORD = "301415"
    
    def __init__(self, db_path: str = "databases/pymoo.db"):
        self.db_path = db_path
        self.init_database()
        self.ensure_admin_user()
    
    # initialize the database if not exists
    def init_database(self):
        """Initialize the user database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # create Users table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # create AHP comparisons table if not exists
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
        
        # create TOPSIS weights table if not exists
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
        
        # create Group sessions table if not exists
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
    
    def ensure_admin_user(self):
        """Ensure the admin user exists"""
        if not self.user_exists(self.ADMIN_USERNAME):
            self._create_admin_user()
    
    def _create_admin_user(self):
        """Create the admin user (internal method)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self._hash_password(self.ADMIN_PASSWORD)
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (self.ADMIN_USERNAME, password_hash, 'admin')
            )
            
            conn.commit()
            conn.close()
            print(f"Admin user created: username='{self.ADMIN_USERNAME}', password='{self.ADMIN_PASSWORD}'")
            return True
        except Exception as e:
            print(f"Error creating admin user: {e}")
            return False
    
    # basic hashing of passwors TODO: improve security
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    
    # create a new user [only callable by SystemAdmin
    def create_regular_user(self, username: str, password: str, admin_username: str) -> bool:
        
        if admin_username != self.ADMIN_USERNAME:
            raise PermissionError("Only admin can create users")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self._hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, 'user')
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
    
    def update_user_role(self, username: str, new_role: str, admin_username: str) -> bool:
        """Update a user's role (only callable by admin)"""
        # Verify that the caller is admin
        if admin_username != self.ADMIN_USERNAME:
            raise PermissionError("Only admin can update user roles")
        
        # Prevent changing the main admin's role
        if username == self.ADMIN_USERNAME:
            raise PermissionError("Cannot change the main admin's role")
        
        # Validate role
        if new_role not in ['user', 'admin']:
            raise ValueError("Role must be 'user' or 'admin'")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET role = ? WHERE username = ?", (new_role, username))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating user role: {e}")
            return False

    def delete_user(self, username: str, admin_username: str) -> bool:
        """Delete a user and all their data (only callable by admin)"""
        # Verify that the caller is admin
        if admin_username != self.ADMIN_USERNAME:
            raise PermissionError("Only admin can delete users")
        
        # Prevent deleting the main admin account only
        if username == self.ADMIN_USERNAME:
            raise PermissionError("Cannot delete the main admin account")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete user's AHP comparisons
            cursor.execute("DELETE FROM ahp_comparisons WHERE username = ?", (username,))
            
            # Delete user's TOPSIS weights  
            cursor.execute("DELETE FROM topsis_weights WHERE username = ?", (username,))
            
            # Delete the user
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    def update_username(self, old_username: str, new_username: str, admin_username: str) -> bool:
        """Update a user's username (only callable by admin)"""
        # Verify that the caller is admin
        if admin_username != self.ADMIN_USERNAME:
            raise PermissionError("Only admin can update usernames")
        
        # Prevent updating admin username this way
        if old_username == self.ADMIN_USERNAME:
            raise PermissionError("Use update_admin_username for admin account")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update username in users table
            cursor.execute("UPDATE users SET username = ? WHERE username = ?", (new_username, old_username))
            
            # Update username in related tables
            cursor.execute("UPDATE ahp_comparisons SET username = ? WHERE username = ?", (new_username, old_username))
            cursor.execute("UPDATE topsis_weights SET username = ? WHERE username = ?", (new_username, old_username))
            cursor.execute("UPDATE group_sessions SET created_by = ? WHERE created_by = ?", (new_username, old_username))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating username: {e}")
            return False
    
    def reset_password(self, username: str, new_password: str, admin_username: str) -> bool:
        """Reset a user's password (only callable by admin)"""
        # Verify that the caller is admin
        if admin_username != self.ADMIN_USERNAME:
            raise PermissionError("Only admin can reset passwords")
        
        # Prevent resetting admin password this way
        if username == self.ADMIN_USERNAME:
            raise PermissionError("Use update_admin_password for admin account")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self._hash_password(new_password)
            cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (password_hash, username))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error resetting password: {e}")
            return False
    
    def update_admin_username(self, old_username: str, new_username: str, current_password: str) -> bool:
        """Update admin username (requires current password verification)"""
        # Verify current password
        if not self.verify_user(old_username, current_password):
            raise PermissionError("Current password is incorrect")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update username in users table
            cursor.execute("UPDATE users SET username = ? WHERE username = ? AND role = 'admin'", (new_username, old_username))
            
            # Update username in related tables
            cursor.execute("UPDATE ahp_comparisons SET username = ? WHERE username = ?", (new_username, old_username))
            cursor.execute("UPDATE topsis_weights SET username = ? WHERE username = ?", (new_username, old_username))
            cursor.execute("UPDATE group_sessions SET created_by = ? WHERE created_by = ?", (new_username, old_username))
            
            conn.commit()
            conn.close()
            
            # Update the class constant
            self.ADMIN_USERNAME = new_username
            return True
        except Exception as e:
            print(f"Error updating admin username: {e}")
            return False
    
    def update_admin_password(self, username: str, new_password: str, current_password: str) -> bool:
        """Update admin password (requires current password verification)"""
        # Verify current password
        if not self.verify_user(username, current_password):
            raise PermissionError("Current password is incorrect")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self._hash_password(new_password)
            cursor.execute("UPDATE users SET password_hash = ? WHERE username = ? AND role = 'admin'", (password_hash, username))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating admin password: {e}")
            return False
    
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