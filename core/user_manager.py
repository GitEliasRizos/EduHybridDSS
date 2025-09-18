"""
User Database Manager for PyMOO GUI Multi-User System
=====================================================

This module manages user data, authentication, and group decision making data storage.
"""

import sqlite3
import hashlib
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import numpy as np


class UserDatabaseManager:
    """
    Manages user database operations for group decision making system
    
    Features:
    - User authentication and registration
    - Criteria comparison storage for AHP/TOPSIS
    - Group aggregation of user inputs
    - Session management
    """
    
    def __init__(self, db_path: str = "pymoo_users.db"):
        """Initialize database manager"""
        self.db_path = db_path
        self.current_session = None
        self._init_database()
        self._create_default_admin()
        
    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('admin', 'user')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT UNIQUE NOT NULL,
                    problem_name TEXT,
                    criteria_names TEXT,  -- JSON array
                    objectives_info TEXT, -- JSON array
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            """)
            
            # AHP comparisons table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ahp_comparisons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    user_id INTEGER,
                    comparison_matrix TEXT,  -- JSON serialized matrix
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(session_id, user_id)
                )
            """)
            
            # TOPSIS weights table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS topsis_weights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    user_id INTEGER,
                    weights TEXT,  -- JSON array
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(session_id, user_id)
                )
            """)
            
            # Group results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS group_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    method TEXT CHECK (method IN ('ahp', 'topsis')),
                    aggregated_data TEXT,  -- JSON serialized results
                    final_scores TEXT,     -- JSON array
                    final_rankings TEXT,   -- JSON array
                    computed_by INTEGER,
                    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id),
                    FOREIGN KEY (computed_by) REFERENCES users (id)
                )
            """)
            
            conn.commit()
            
    def _create_default_admin(self):
        """Create default admin user if not exists"""
        try:
            self.register_user("admin", "admin123", "System Administrator", "admin")
        except ValueError:
            pass  # Admin already exists
            
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
        
    def register_user(self, username: str, password: str, full_name: str, role: str) -> bool:
        """Register a new user"""
        if role not in ['admin', 'user']:
            raise ValueError("Role must be 'admin' or 'user'")
            
        password_hash = self._hash_password(password)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (username, password_hash, full_name, role)
                    VALUES (?, ?, ?, ?)
                """, (username, password_hash, full_name, role))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            raise ValueError(f"Username '{username}' already exists")
            
    def authenticate_user(self, username: str, password: str, role: str) -> Optional[Dict]:
        """Authenticate user and return user data"""
        password_hash = self._hash_password(password)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, full_name, role 
                FROM users 
                WHERE username = ? AND password_hash = ? AND role = ? AND is_active = 1
            """, (username, password_hash, role))
            
            result = cursor.fetchone()
            if result:
                # Update last login
                cursor.execute("""
                    UPDATE users SET last_login = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (result[0],))
                conn.commit()
                
                return {
                    'id': result[0],
                    'username': result[1],
                    'full_name': result[2],
                    'role': result[3]
                }
        return None
        
    def create_session(self, session_name: str, problem_name: str, 
                      criteria_names: List[str], objectives_info: List[Dict],
                      created_by_user_id: int) -> int:
        """Create a new decision making session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (session_name, problem_name, criteria_names, 
                                    objectives_info, created_by)
                VALUES (?, ?, ?, ?, ?)
            """, (session_name, problem_name, json.dumps(criteria_names), 
                  json.dumps(objectives_info), created_by_user_id))
            
            session_id = cursor.lastrowid
            conn.commit()
            return session_id
            
    def get_active_sessions(self) -> List[Dict]:
        """Get all active sessions"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.id, s.session_name, s.problem_name, s.criteria_names,
                       s.objectives_info, s.created_at, u.full_name as created_by_name
                FROM sessions s
                JOIN users u ON s.created_by = u.id
                WHERE s.is_active = 1
                ORDER BY s.created_at DESC
            """)
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'id': row[0],
                    'session_name': row[1],
                    'problem_name': row[2],
                    'criteria_names': json.loads(row[3]),
                    'objectives_info': json.loads(row[4]),
                    'created_at': row[5],
                    'created_by_name': row[6]
                })
            return sessions
            
    def submit_ahp_comparison(self, session_id: int, user_id: int, 
                             comparison_matrix: np.ndarray) -> bool:
        """Submit AHP pairwise comparison matrix"""
        # Convert numpy array to list for JSON serialization
        matrix_list = comparison_matrix.tolist()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO ahp_comparisons 
                (session_id, user_id, comparison_matrix)
                VALUES (?, ?, ?)
            """, (session_id, user_id, json.dumps(matrix_list)))
            conn.commit()
            return True
            
    def submit_topsis_weights(self, session_id: int, user_id: int, 
                             weights: List[float]) -> bool:
        """Submit TOPSIS weights"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO topsis_weights 
                (session_id, user_id, weights)
                VALUES (?, ?, ?)
            """, (session_id, user_id, json.dumps(weights)))
            conn.commit()
            return True
            
    def get_session_ahp_comparisons(self, session_id: int) -> Dict[str, np.ndarray]:
        """Get all AHP comparisons for a session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.username, a.comparison_matrix
                FROM ahp_comparisons a
                JOIN users u ON a.user_id = u.id
                WHERE a.session_id = ?
            """, (session_id,))
            
            comparisons = {}
            for username, matrix_json in cursor.fetchall():
                matrix_list = json.loads(matrix_json)
                comparisons[username] = np.array(matrix_list)
            return comparisons
            
    def get_session_topsis_weights(self, session_id: int) -> Dict[str, List[float]]:
        """Get all TOPSIS weights for a session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.username, t.weights
                FROM topsis_weights t
                JOIN users u ON t.user_id = u.id
                WHERE t.session_id = ?
            """, (session_id,))
            
            weights = {}
            for username, weights_json in cursor.fetchall():
                weights[username] = json.loads(weights_json)
            return weights
            
    def aggregate_ahp_matrices(self, matrices: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Aggregate AHP matrices using geometric mean method
        
        This is the standard approach for AHP group decision making:
        For each matrix element (i,j): geometric_mean = (a1_ij × a2_ij × ... × an_ij)^(1/n)
        """
        if not matrices:
            raise ValueError("No matrices to aggregate")
            
        # Get matrix dimensions from first matrix
        first_matrix = next(iter(matrices.values()))
        n = first_matrix.shape[0]
        
        # Initialize result matrix
        aggregated = np.ones((n, n))
        
        # Calculate geometric mean for each element
        for i in range(n):
            for j in range(n):
                if i != j:  # Skip diagonal elements (they remain 1)
                    elements = [matrix[i, j] for matrix in matrices.values()]
                    # Geometric mean: (a1 × a2 × ... × an)^(1/n)
                    geometric_mean = np.power(np.prod(elements), 1.0 / len(elements))
                    aggregated[i, j] = geometric_mean
                    aggregated[j, i] = 1.0 / geometric_mean  # Reciprocal property
                    
        return aggregated
        
    def aggregate_topsis_weights(self, weights_dict: Dict[str, List[float]]) -> List[float]:
        """
        Aggregate TOPSIS weights using arithmetic mean
        """
        if not weights_dict:
            raise ValueError("No weights to aggregate")
            
        # Convert to numpy array for easier calculation
        weights_arrays = [np.array(weights) for weights in weights_dict.values()]
        weights_matrix = np.stack(weights_arrays)
        
        # Calculate arithmetic mean
        aggregated_weights = np.mean(weights_matrix, axis=0)
        
        # Normalize to sum to 1
        aggregated_weights = aggregated_weights / np.sum(aggregated_weights)
        
        return aggregated_weights.tolist()
        
    def save_group_result(self, session_id: int, method: str, 
                         aggregated_data: Any, final_scores: List[float],
                         final_rankings: List[int], computed_by_user_id: int) -> bool:
        """Save group decision making results"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO group_results 
                (session_id, method, aggregated_data, final_scores, 
                 final_rankings, computed_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, method, json.dumps(aggregated_data, default=str),
                  json.dumps(final_scores), json.dumps(final_rankings),
                  computed_by_user_id))
            conn.commit()
            return True
            
    def get_group_results(self, session_id: int, method: str) -> Optional[Dict]:
        """Get group decision making results"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT aggregated_data, final_scores, final_rankings, 
                       computed_at, u.full_name
                FROM group_results gr
                JOIN users u ON gr.computed_by = u.id
                WHERE gr.session_id = ? AND gr.method = ?
                ORDER BY gr.computed_at DESC
                LIMIT 1
            """, (session_id, method))
            
            result = cursor.fetchone()
            if result:
                return {
                    'aggregated_data': json.loads(result[0]),
                    'final_scores': json.loads(result[1]),
                    'final_rankings': json.loads(result[2]),
                    'computed_at': result[3],
                    'computed_by': result[4]
                }
        return None
        
    def get_session_participation(self, session_id: int) -> Dict:
        """Get participation statistics for a session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get total users
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1 AND role = 'user'")
            total_users = cursor.fetchone()[0]
            
            # Get AHP participants
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) FROM ahp_comparisons 
                WHERE session_id = ?
            """, (session_id,))
            ahp_participants = cursor.fetchone()[0]
            
            # Get TOPSIS participants
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) FROM topsis_weights 
                WHERE session_id = ?
            """, (session_id,))
            topsis_participants = cursor.fetchone()[0]
            
            return {
                'total_users': total_users,
                'ahp_participants': ahp_participants,
                'topsis_participants': topsis_participants,
                'ahp_participation_rate': ahp_participants / max(total_users, 1) * 100,
                'topsis_participation_rate': topsis_participants / max(total_users, 1) * 100
            }
            
    def get_user_submissions(self, session_id: int, user_id: int) -> Dict:
        """Check what submissions a user has made for a session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check AHP submission
            cursor.execute("""
                SELECT submitted_at FROM ahp_comparisons 
                WHERE session_id = ? AND user_id = ?
            """, (session_id, user_id))
            ahp_submission = cursor.fetchone()
            
            # Check TOPSIS submission
            cursor.execute("""
                SELECT submitted_at FROM topsis_weights 
                WHERE session_id = ? AND user_id = ?
            """, (session_id, user_id))
            topsis_submission = cursor.fetchone()
            
            return {
                'has_ahp_submission': ahp_submission is not None,
                'ahp_submitted_at': ahp_submission[0] if ahp_submission else None,
                'has_topsis_submission': topsis_submission is not None,
                'topsis_submitted_at': topsis_submission[0] if topsis_submission else None
            }
            
    def close(self):
        """Close database connections"""
        # SQLite connections are automatically managed by context managers
        pass