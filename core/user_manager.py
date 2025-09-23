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
    
    def __init__(self, db_path: str = "databases/pymoo.db"):
        """Initialize database manager"""
        self.db_path = db_path
        self.current_session = None
        self._init_database()
        self._migrate_database()  # Apply any schema updates
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
                    optimization_results TEXT, -- JSON serialized optimization results
                    alternatives_data TEXT,    -- JSON array of alternatives for decision making
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
                    method TEXT CHECK (method IN ('ahp', 'topsis', 'consensus')),
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
    
    def _migrate_database(self):
        """Migrate database schema to latest version"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if new columns exist in sessions table
            cursor.execute("PRAGMA table_info(sessions)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            # Add optimization_results column if it doesn't exist
            if 'optimization_results' not in column_names:
                print("Adding optimization_results column to sessions table...")
                cursor.execute("""
                    ALTER TABLE sessions 
                    ADD COLUMN optimization_results TEXT
                """)
                print("✅ optimization_results column added")
            
            # Add alternatives_data column if it doesn't exist
            if 'alternatives_data' not in column_names:
                print("Adding alternatives_data column to sessions table...")
                cursor.execute("""
                    ALTER TABLE sessions 
                    ADD COLUMN alternatives_data TEXT
                """)
                print("✅ alternatives_data column added")
            
            # Update group_results table constraint to include 'consensus'
            cursor.execute("PRAGMA table_info(group_results)")
            group_results_columns = cursor.fetchall()
            
            if group_results_columns:  # Table exists
                # Check current constraint by trying to insert 'consensus'
                try:
                    cursor.execute("INSERT INTO group_results (session_id, method, aggregated_data, final_scores, final_rankings, computed_by) VALUES (999, 'consensus', '{}', '[]', '[]', 1)")
                    cursor.execute("DELETE FROM group_results WHERE session_id = 999")  # Clean up test
                    print("group_results table already supports 'consensus' method")
                except sqlite3.IntegrityError:
                    print("Updating group_results table to support 'consensus' method...")
                    
                    # Backup existing data
                    cursor.execute("SELECT * FROM group_results")
                    existing_data = cursor.fetchall()
                    
                    # Drop and recreate table with updated constraint
                    cursor.execute("DROP TABLE group_results")
                    cursor.execute("""
                        CREATE TABLE group_results (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            session_id INTEGER,
                            method TEXT CHECK (method IN ('ahp', 'topsis', 'consensus')),
                            aggregated_data TEXT,
                            final_scores TEXT,
                            final_rankings TEXT,
                            computed_by INTEGER,
                            computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (session_id) REFERENCES sessions (id),
                            FOREIGN KEY (computed_by) REFERENCES users (id)
                        )
                    """)
                    
                    # Restore data
                    for row in existing_data:
                        cursor.execute("""
                            INSERT INTO group_results 
                            (id, session_id, method, aggregated_data, final_scores, final_rankings, computed_by, computed_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, row)
                    
                    print("group_results table updated successfully")
            
            # Migrate problem_name to problem_description in sessions table
            cursor.execute("PRAGMA table_info(sessions)")
            sessions_columns = [col[1] for col in cursor.fetchall()]
            
            if 'problem_name' in sessions_columns and 'problem_description' not in sessions_columns:
                print("Migrating sessions table: problem_name -> problem_description...")
                
                # Add new column
                cursor.execute("""
                    ALTER TABLE sessions 
                    ADD COLUMN problem_description TEXT
                """)
                
                # Copy data from old column to new column
                cursor.execute("""
                    UPDATE sessions 
                    SET problem_description = problem_name
                    WHERE problem_name IS NOT NULL
                """)
                
                # Note: SQLite doesn't support dropping columns directly
                # We'll keep the old column for backward compatibility
                # but the application will use problem_description
                
                print("✅ problem_description column added and data migrated")
            elif 'problem_description' in sessions_columns:
                print("Sessions table already has problem_description column")
            
            conn.commit()
            print("Database migration completed successfully!")
            
    def _create_default_admin(self):
        """Create default admin user if not exists"""
        try:
            self.register_user("iiooooiooi", "301415", "System Administrator", "admin")
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
    
    def _make_json_serializable(self, obj):
        """Convert numpy arrays and other non-serializable objects to JSON-compatible format"""
        import numpy as np
        
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, tuple):
            return list(self._make_json_serializable(list(obj)))
        elif isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32)):
            return float(obj)
        elif hasattr(obj, 'item'):  # numpy scalars
            return obj.item()
        else:
            return obj
        
    def create_session(self, session_name: str, problem_description: str, 
                      criteria_names: List[str], objectives_info: List[Dict],
                      created_by_user_id: int, optimization_results: Dict = None,
                      alternatives_data: List[Dict] = None) -> int:
        """Create a new decision making session with optional optimization results"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Convert to JSON-serializable format
            serializable_optimization_results = None
            if optimization_results:
                serializable_optimization_results = self._make_json_serializable(optimization_results)
            
            serializable_alternatives_data = None
            if alternatives_data:
                serializable_alternatives_data = self._make_json_serializable(alternatives_data)
            
            cursor.execute("""
                INSERT INTO sessions (session_name, problem_description, criteria_names, 
                                    objectives_info, optimization_results, alternatives_data, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_name, problem_description, json.dumps(criteria_names), 
                  json.dumps(objectives_info), 
                  json.dumps(serializable_optimization_results) if serializable_optimization_results else None,
                  json.dumps(serializable_alternatives_data) if serializable_alternatives_data else None,
                  created_by_user_id))
            
            session_id = cursor.lastrowid
            conn.commit()
            return session_id
            
    def get_active_sessions(self) -> List[Dict]:
        """Get all active sessions"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.id, s.session_name, 
                       COALESCE(s.problem_description, s.problem_name) as problem_description,
                       s.criteria_names, s.objectives_info, s.optimization_results, s.alternatives_data,
                       s.created_at, u.full_name as created_by_name
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
                    'problem_description': row[2],
                    'criteria_names': json.loads(row[3]) if row[3] else [],
                    'objectives_info': json.loads(row[4]) if row[4] else [],
                    'optimization_results': json.loads(row[5]) if row[5] else None,
                    'alternatives_data': json.loads(row[6]) if row[6] else None,
                    'created_at': row[7],
                    'created_by_name': row[8]
                })
            return sessions
    
    def update_session_optimization_results(self, session_id: int, optimization_results: Dict, 
                                           alternatives_data: List[Dict] = None) -> bool:
        """Update an existing session with optimization results and alternatives data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE sessions 
                    SET optimization_results = ?, alternatives_data = ?
                    WHERE id = ?
                """, (json.dumps(optimization_results),
                      json.dumps(alternatives_data) if alternatives_data else None,
                      session_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating session optimization results: {e}")
            return False
    
    def get_session_optimization_results(self, session_id: int) -> Tuple[Dict, List[Dict]]:
        """Get optimization results and alternatives data for a session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT optimization_results, alternatives_data
                FROM sessions 
                WHERE id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            if row:
                opt_results = json.loads(row[0]) if row[0] else {}
                alternatives = json.loads(row[1]) if row[1] else []
                return opt_results, alternatives
            return {}, []
            
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
        print(f"Debug get_session_topsis_weights: session_id: {session_id}")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.username, t.weights
                FROM topsis_weights t
                JOIN users u ON t.user_id = u.id
                WHERE t.session_id = ?
            """, (session_id,))
            
            rows = cursor.fetchall()
            print(f"Debug get_session_topsis_weights: found {len(rows)} TOPSIS weight entries")
            
            weights = {}
            for i, (username, weights_json) in enumerate(rows):
                print(f"Debug get_session_topsis_weights: processing entry {i}: user={username}")
                print(f"Debug get_session_topsis_weights: weights_json type: {type(weights_json)}")
                print(f"Debug get_session_topsis_weights: weights_json content: {weights_json}")
                
                try:
                    weights[username] = json.loads(weights_json)
                    print(f"Debug get_session_topsis_weights: parsed weights for {username}: {weights[username]}")
                except Exception as e:
                    print(f"Debug get_session_topsis_weights: Error parsing JSON for {username}: {e}")
                    
            print(f"Debug get_session_topsis_weights: final weights dict: {weights}")
            return weights
    
    def get_session_status(self, session_id: int) -> Dict:
        """Get comprehensive status information for a session"""
        try:
            # Get session details
            sessions = self.get_active_sessions()
            session = next((s for s in sessions if s['id'] == session_id), None)
            
            if not session:
                return {'error': 'Session not found'}
            
            # Get user submissions
            ahp_submissions = self.get_session_ahp_comparisons(session_id)
            topsis_submissions = self.get_session_topsis_weights(session_id)
            
            # Get all active users
            all_users = self.get_all_users()
            regular_users = [u for u in all_users if u['role'] == 'user']
            
            # Calculate participation rates
            total_users = len(regular_users)
            ahp_participants = len(ahp_submissions)
            topsis_participants = len(topsis_submissions)
            
            status = {
                'session_id': session_id,
                'session_name': session['session_name'],
                'total_users': total_users,
                'ahp_submissions': ahp_participants,
                'topsis_submissions': topsis_participants,
                'ahp_participation_rate': (ahp_participants / total_users * 100) if total_users > 0 else 0,
                'topsis_participation_rate': (topsis_participants / total_users * 100) if total_users > 0 else 0,
                'has_optimization_results': session['optimization_results'] is not None,
                'alternatives_count': len(session['alternatives_data']) if session['alternatives_data'] else 0,
                'criteria_count': len(session['criteria_names']),
                'ready_for_ahp_analysis': ahp_participants >= 2,  # Need at least 2 participants
                'ready_for_topsis_analysis': topsis_participants >= 2,
                'participants': {
                    'ahp': list(ahp_submissions.keys()),
                    'topsis': list(topsis_submissions.keys())
                }
            }
            
            return status
            
        except Exception as e:
            return {'error': f'Failed to get session status: {str(e)}'}
    
    def get_all_sessions_status(self) -> List[Dict]:
        """Get status for all active sessions"""
        sessions = self.get_active_sessions()
        status_list = []
        
        for session in sessions:
            status = self.get_session_status(session['id'])
            status_list.append(status)
        
        return status_list
    
    def get_pending_sessions(self, min_participants: int = 2) -> List[Dict]:
        """Get sessions that have enough participants for group analysis"""
        all_status = self.get_all_sessions_status()
        
        pending_sessions = []
        for status in all_status:
            if 'error' not in status:
                if (status['ready_for_ahp_analysis'] or status['ready_for_topsis_analysis']):
                    pending_sessions.append(status)
        
        return pending_sessions
            
    def aggregate_ahp_matrices(self, matrices: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Aggregate AHP matrices using geometric mean method
        
        This is the standard approach for AHP group decision making:
        For each matrix element (i,j): geometric_mean = (a1_ij × a2_ij × ... × an_ij)^(1/n)
        """
        print(f"Debug aggregate_ahp_matrices: input matrices type: {type(matrices)}")
        if not matrices:
            raise ValueError("No matrices to aggregate")
            
        print(f"Debug aggregate_ahp_matrices: matrices keys: {list(matrices.keys())}")
        print(f"Debug aggregate_ahp_matrices: matrices count: {len(matrices)}")
        
        # Get matrix dimensions from first matrix
        first_matrix = next(iter(matrices.values()))
        print(f"Debug aggregate_ahp_matrices: first matrix shape: {first_matrix.shape}")
        print(f"Debug aggregate_ahp_matrices: first matrix type: {type(first_matrix)}")
        n = first_matrix.shape[0]
        
        # Initialize result matrix
        aggregated = np.ones((n, n))
        print(f"Debug aggregate_ahp_matrices: initialized aggregated matrix shape: {aggregated.shape}")
        
        # Calculate geometric mean for each element
        for i in range(n):
            for j in range(n):
                if i != j:  # Skip diagonal elements (they remain 1)
                    try:
                        elements = [matrix[i, j] for matrix in matrices.values()]
                        print(f"Debug aggregate: Processing ({i},{j}), elements: {elements}")
                        
                        if not elements:
                            raise ValueError(f"No elements found for position ({i},{j})")
                        
                        # Geometric mean: (a1 × a2 × ... × an)^(1/n)
                        geometric_mean = np.power(np.prod(elements), 1.0 / len(elements))
                        aggregated[i, j] = geometric_mean
                        aggregated[j, i] = 1.0 / geometric_mean  # Reciprocal property
                        
                    except Exception as e:
                        print(f"Debug aggregate: Error at position ({i},{j}): {e}")
                        print(f"Debug aggregate: matrices.values() type: {type(matrices.values())}")
                        print(f"Debug aggregate: matrices.values(): {list(matrices.values())}")
                        raise
        
        print(f"Debug aggregate_ahp_matrices: final aggregated matrix shape: {aggregated.shape}")
        print(f"Debug aggregate_ahp_matrices: final aggregated matrix:\n{aggregated}")
        return aggregated
        
    def aggregate_topsis_weights(self, weights_dict: Dict[str, List[float]]) -> List[float]:
        """
        Aggregate TOPSIS weights using arithmetic mean
        """
        print(f"Debug aggregate_topsis_weights: input weights_dict type: {type(weights_dict)}")
        if not weights_dict:
            raise ValueError("No weights to aggregate")
            
        print(f"Debug aggregate_topsis_weights: weights_dict keys: {list(weights_dict.keys())}")
        print(f"Debug aggregate_topsis_weights: weights_dict count: {len(weights_dict)}")
        
        # Convert to numpy array for easier calculation
        try:
            weights_arrays = [np.array(weights) for weights in weights_dict.values()]
            print(f"Debug aggregate_topsis_weights: created {len(weights_arrays)} weight arrays")
            
            if not weights_arrays:
                raise ValueError("No weight arrays created")
                
            # Check if weights_dict.values() might be None
            weights_values = weights_dict.values()
            print(f"Debug aggregate_topsis_weights: weights_dict.values() type: {type(weights_values)}")
            print(f"Debug aggregate_topsis_weights: weights_dict.values(): {list(weights_values)}")
            
            weights_matrix = np.stack(weights_arrays)
            print(f"Debug aggregate_topsis_weights: weights_matrix shape: {weights_matrix.shape}")
            
        except Exception as e:
            print(f"Debug aggregate_topsis_weights: Error creating arrays: {e}")
            print(f"Debug aggregate_topsis_weights: weights_dict content: {weights_dict}")
            raise
        
        # Calculate arithmetic mean
        aggregated_weights = np.mean(weights_matrix, axis=0)
        print(f"Debug aggregate_topsis_weights: aggregated_weights before normalization: {aggregated_weights}")
        
        # Normalize to sum to 1
        aggregated_weights = aggregated_weights / np.sum(aggregated_weights)
        print(f"Debug aggregate_topsis_weights: final aggregated_weights: {aggregated_weights}")
        
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
    
    def compute_group_decision(self, session_id: int, computed_by_user_id: int) -> Dict:
        """
        Complete group decision computation - aggregates all user inputs and computes final rankings
        
        Returns:
            Dict containing:
            - ahp_results: AHP-based rankings and scores
            - topsis_results: TOPSIS-based rankings and scores  
            - consensus_results: Combined consensus rankings
            - participation_stats: Information about user participation
        """
        
        # Get session information
        sessions = self.get_active_sessions()
        session = next((s for s in sessions if s['id'] == session_id), None)
        if not session:
            raise ValueError(f"Session {session_id} not found")
            
        # Get alternatives data from session
        alternatives_data = session.get('alternatives_data', [])
        if not alternatives_data:
            raise ValueError("No alternatives data found in session")
            
        # Get all user submissions
        ahp_matrices = self.get_session_ahp_comparisons(session_id)
        topsis_weights = self.get_session_topsis_weights(session_id)
        
        results = {
            'session_id': session_id,
            'session_name': session['session_name'],
            'alternatives_count': len(alternatives_data),
            'ahp_participants': len(ahp_matrices),
            'topsis_participants': len(topsis_weights),
            'computed_at': datetime.now().isoformat()
        }
        
        # Compute AHP-based group decision
        if ahp_matrices:
            ahp_result = self._compute_ahp_group_decision(ahp_matrices, alternatives_data)
            results['ahp_results'] = ahp_result
            
            # Save AHP results to database
            self.save_group_result(
                session_id=session_id,
                method='AHP',
                aggregated_data=ahp_result['aggregated_matrix'].tolist(),
                final_scores=ahp_result['final_scores'],
                final_rankings=ahp_result['rankings'],
                computed_by_user_id=computed_by_user_id
            )
        
        # Compute TOPSIS-based group decision
        if topsis_weights:
            topsis_result = self._compute_topsis_group_decision(topsis_weights, alternatives_data, session)
            results['topsis_results'] = topsis_result
            
            # Save TOPSIS results to database
            self.save_group_result(
                session_id=session_id,
                method='TOPSIS',
                aggregated_data=topsis_result['aggregated_weights'],
                final_scores=topsis_result['final_scores'],
                final_rankings=topsis_result['rankings'],
                computed_by_user_id=computed_by_user_id
            )
        
        # Compute consensus ranking if both methods available
        if ahp_matrices and topsis_weights:
            consensus_result = self._compute_consensus_ranking(
                results['ahp_results'], results['topsis_results']
            )
            results['consensus_results'] = consensus_result
            
            # Save consensus results
            self.save_group_result(
                session_id=session_id,
                method='consensus',
                aggregated_data=consensus_result,
                final_scores=consensus_result['combined_scores'],
                final_rankings=consensus_result['final_rankings'],
                computed_by_user_id=computed_by_user_id
            )
        
        return results
    
    def _compute_ahp_group_decision(self, ahp_matrices: Dict[str, np.ndarray], 
                                   alternatives_data: List[Dict]) -> Dict:
        """Compute group decision using aggregated AHP matrices"""
        
        print(f"Debug AHP: ahp_matrices type: {type(ahp_matrices)}, length: {len(ahp_matrices) if ahp_matrices else 'None'}")
        print(f"Debug AHP: alternatives_data type: {type(alternatives_data)}, length: {len(alternatives_data) if alternatives_data else 'None'}")
        
        if not ahp_matrices:
            raise ValueError("No AHP matrices provided")
        
        if not alternatives_data:
            raise ValueError("No alternatives data provided")
        
        # Aggregate all AHP matrices using geometric mean
        aggregated_matrix = self.aggregate_ahp_matrices(ahp_matrices)
        print(f"Debug AHP: aggregated_matrix returned: {aggregated_matrix is not None}")
        print(f"Debug AHP: aggregated_matrix shape: {aggregated_matrix.shape if aggregated_matrix is not None else 'None'}")
        
        # Compute weights from aggregated matrix using eigenvalue method
        try:
            eigenvalues, eigenvectors = np.linalg.eig(aggregated_matrix)
            print(f"Debug AHP: eigenvalues shape: {eigenvalues.shape}")
            print(f"Debug AHP: eigenvectors shape: {eigenvectors.shape}")
            
            max_eigenvalue_index = np.argmax(eigenvalues.real)
            principal_eigenvector = eigenvectors[:, max_eigenvalue_index].real
            print(f"Debug AHP: principal_eigenvector shape: {principal_eigenvector.shape}")
            
        except Exception as e:
            print(f"Debug AHP: Error in eigenvalue computation: {e}")
            raise
        
        # Normalize weights to sum to 1
        weights = principal_eigenvector / np.sum(principal_eigenvector)
        weights = np.abs(weights)  # Ensure positive weights
        weights = weights / np.sum(weights)  # Renormalize
        
        # Apply weights to alternatives
        alternative_scores = []
        for i, alt in enumerate(alternatives_data):
            print(f"Debug AHP: Processing alternative {i}: {alt}")
            
            if 'values' not in alt:
                raise ValueError(f"Alternative {i} missing 'values' field")
            
            values = np.array(alt['values'])
            print(f"Debug AHP: Alternative {i} values: {values}, shape: {values.shape}")
            
            # Normalize values (higher is better) - avoid division by zero
            max_values = np.max(values) if np.max(values) > 0 else 1
            normalized_values = values / max_values
            score = np.sum(weights * normalized_values)
            alternative_scores.append(score)
        
        print(f"Debug AHP: alternative_scores: {alternative_scores}")
        print(f"Debug AHP: alternative_scores type: {type(alternative_scores)}")
        print(f"Debug AHP: alternative_scores length: {len(alternative_scores)}")
        
        if not alternative_scores:
            raise ValueError("No alternative scores computed")
        
        # Create rankings (1 = best, 2 = second best, etc.)
        try:
            rankings = np.argsort(np.argsort(alternative_scores)[::-1]) + 1
            print(f"Debug AHP: rankings computed successfully: {rankings}")
        except Exception as e:
            print(f"Debug AHP: Error computing rankings: {e}")
            print(f"Debug AHP: alternative_scores when error: {alternative_scores}")
            raise
        
        # Compute consistency ratio
        n = len(weights)
        consistency_index = (np.max(eigenvalues.real) - n) / (n - 1) if n > 1 else 0
        
        # Random Index values for consistency checking
        random_indices = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
        random_index = random_indices.get(n, 1.49)
        consistency_ratio = consistency_index / random_index if random_index > 0 else 0
        
        return {
            'method': 'AHP',
            'aggregated_matrix': aggregated_matrix,
            'criteria_weights': weights.tolist(),
            'final_scores': alternative_scores,
            'rankings': rankings.tolist(),
            'consistency_ratio': consistency_ratio,
            'is_consistent': consistency_ratio < 0.1,
            'participants': len(ahp_matrices)
        }
    
    def _compute_topsis_group_decision(self, topsis_weights: Dict[str, List[float]], 
                                      alternatives_data: List[Dict], session: Dict) -> Dict:
        """Compute group decision using aggregated TOPSIS weights"""
        
        print(f"Debug TOPSIS: topsis_weights type: {type(topsis_weights)}, length: {len(topsis_weights) if topsis_weights else 'None'}")
        print(f"Debug TOPSIS: alternatives_data type: {type(alternatives_data)}, length: {len(alternatives_data) if alternatives_data else 'None'}")
        print(f"Debug TOPSIS: session type: {type(session)}")
        
        if not topsis_weights:
            raise ValueError("No TOPSIS weights provided")
        
        if not alternatives_data:
            raise ValueError("No alternatives data provided")
        
        # Aggregate TOPSIS weights
        try:
            aggregated_weights = self.aggregate_topsis_weights(topsis_weights)
            print(f"Debug TOPSIS: aggregated_weights: {aggregated_weights}")
            print(f"Debug TOPSIS: aggregated_weights type: {type(aggregated_weights)}")
        except Exception as e:
            print(f"Debug TOPSIS: Error in weight aggregation: {e}")
            raise
        
        # Prepare decision matrix from alternatives
        try:
            decision_matrix = []
            for i, alt in enumerate(alternatives_data):
                print(f"Debug TOPSIS: Processing alternative {i}: {alt}")
                if 'values' not in alt:
                    raise ValueError(f"Alternative {i} missing 'values' field")
                decision_matrix.append(alt['values'])
                
            print(f"Debug TOPSIS: decision_matrix length: {len(decision_matrix)}")
            decision_matrix = np.array(decision_matrix)
            print(f"Debug TOPSIS: decision_matrix shape: {decision_matrix.shape}")
            
        except Exception as e:
            print(f"Debug TOPSIS: Error preparing decision matrix: {e}")
            raise
        
        # Normalize decision matrix (vector normalization)
        normalized_matrix = decision_matrix / np.sqrt(np.sum(decision_matrix**2, axis=0))
        
        # Apply weights
        weighted_matrix = normalized_matrix * np.array(aggregated_weights)
        
        # Identify ideal and anti-ideal solutions
        # Assume all objectives are to be maximized (higher is better)
        ideal_solution = np.max(weighted_matrix, axis=0)
        anti_ideal_solution = np.min(weighted_matrix, axis=0)
        
        # Calculate distances
        final_scores = []
        for i, alt_values in enumerate(weighted_matrix):
            # Distance to ideal solution
            d_plus = np.sqrt(np.sum((alt_values - ideal_solution)**2))
            # Distance to anti-ideal solution  
            d_minus = np.sqrt(np.sum((alt_values - anti_ideal_solution)**2))
            
            # Relative closeness to ideal solution
            closeness = d_minus / (d_plus + d_minus) if (d_plus + d_minus) > 0 else 0
            final_scores.append(closeness)
        
        # Create rankings (1 = best, 2 = second best, etc.)
        rankings = np.argsort(np.argsort(final_scores)[::-1]) + 1
        
        return {
            'method': 'TOPSIS',
            'aggregated_weights': aggregated_weights,
            'normalized_matrix': normalized_matrix.tolist(),
            'weighted_matrix': weighted_matrix.tolist(),
            'ideal_solution': ideal_solution.tolist(),
            'anti_ideal_solution': anti_ideal_solution.tolist(),
            'final_scores': final_scores,
            'rankings': rankings.tolist(),
            'participants': len(topsis_weights)
        }
    
    def _compute_consensus_ranking(self, ahp_results: Dict, topsis_results: Dict) -> Dict:
        """Compute consensus ranking by combining AHP and TOPSIS results"""
        
        # Normalize scores to 0-1 range for both methods
        ahp_scores = np.array(ahp_results['final_scores'])
        topsis_scores = np.array(topsis_results['final_scores'])
        
        # Normalize to 0-1 range
        ahp_normalized = (ahp_scores - np.min(ahp_scores)) / (np.max(ahp_scores) - np.min(ahp_scores))
        topsis_normalized = (topsis_scores - np.min(topsis_scores)) / (np.max(topsis_scores) - np.min(topsis_scores))
        
        # Combine with equal weights (could be enhanced with user preferences)
        combined_scores = 0.5 * ahp_normalized + 0.5 * topsis_normalized
        
        # Create final rankings
        final_rankings = np.argsort(np.argsort(combined_scores)[::-1]) + 1
        
        # Calculate correlation between methods
        correlation = np.corrcoef(ahp_scores, topsis_scores)[0, 1]
        
        return {
            'method': 'CONSENSUS',
            'ahp_normalized_scores': ahp_normalized.tolist(),
            'topsis_normalized_scores': topsis_normalized.tolist(),
            'combined_scores': combined_scores.tolist(),
            'final_rankings': final_rankings.tolist(),
            'correlation_coefficient': correlation,
            'agreement_level': 'High' if abs(correlation) > 0.7 else 'Medium' if abs(correlation) > 0.4 else 'Low'
        }
    
    def get_group_results(self, session_id: int) -> Dict[str, Any]:
        """Get all group analysis results for a session"""
        print(f"Debug get_group_results: Fetching results for session {session_id}")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT method, aggregated_data, final_scores, final_rankings, 
                       computed_at, computed_by
                FROM group_results 
                WHERE session_id = ?
                ORDER BY computed_at DESC
            """, (session_id,))
            
            results = cursor.fetchall()
            print(f"Debug get_group_results: Found {len(results)} result entries")
            
            group_results = {}
            for i, result in enumerate(results):
                method = result[0]
                print(f"Debug get_group_results: Processing result {i+1}: method={method}")
                
                try:
                    group_results[method] = {
                        'method': method,
                        'aggregated_data': json.loads(result[1]) if result[1] else None,
                        'final_scores': json.loads(result[2]) if result[2] else None,
                        'final_rankings': json.loads(result[3]) if result[3] else None,
                        'computed_at': result[4],
                        'computed_by': result[5]
                    }
                    print(f"Debug get_group_results: Successfully processed {method}")
                except Exception as e:
                    print(f"Debug get_group_results: Error processing {method}: {e}")
                    raise
            
            print(f"Debug get_group_results: Returning {len(group_results)} methods: {list(group_results.keys())}")
            return group_results
            
    def get_single_group_result(self, session_id: int, method: str) -> Optional[Dict]:
        """Get group decision making results for a specific method"""
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
    
    # Additional methods for user management compatibility
    def get_all_users(self) -> List[Dict[str, str]]:
        """Get all users with their basic info"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username, role, created_at FROM users 
                WHERE is_active = 1 
                ORDER BY created_at
            """)
            results = cursor.fetchall()
            
            return [
                {
                    'username': row[0],
                    'role': row[1], 
                    'created_at': row[2]
                }
                for row in results
            ]
    
    def user_exists(self, username: str) -> bool:
        """Check if user exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE username = ? AND is_active = 1", (username,))
            return cursor.fetchone() is not None
    
    def get_user_role(self, username: str) -> Optional[str]:
        """Get user role"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE username = ? AND is_active = 1", (username,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def verify_user(self, username: str, password: str) -> bool:
        """Verify user credentials (for any role)"""
        password_hash = self._hash_password(password)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM users 
                WHERE username = ? AND password_hash = ? AND is_active = 1
            """, (username, password_hash))
            return cursor.fetchone() is not None
    
    def create_regular_user(self, username: str, password: str, admin_username: str) -> bool:
        """Create a new regular user (only callable by admin)"""
        if admin_username != "iiooooiooi":  # admin check
            raise PermissionError("Only admin can create users")
        
        try:
            return self.register_user(username, password, username, 'user')
        except ValueError:
            return False
    
    def delete_user(self, username: str, admin_username: str) -> bool:
        """Delete a user (only callable by admin)"""
        if admin_username != "iiooooiooi":  # admin check
            raise PermissionError("Only admin can delete users")
        
        if username == "iiooooiooi":  # protect main admin
            raise PermissionError("Cannot delete the main admin account")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Soft delete - mark as inactive
                cursor.execute("UPDATE users SET is_active = 0 WHERE username = ?", (username,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False
    
    def update_username(self, old_username: str, new_username: str, admin_username: str) -> bool:
        """Update username (only callable by admin)"""
        if admin_username != "iiooooiooi":
            raise PermissionError("Only admin can update usernames")
        
        if old_username == "iiooooiooi":
            raise PermissionError("Use update_admin_username for admin account")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET username = ? WHERE username = ?", (new_username, old_username))
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False
    
    def update_password(self, username: str, new_password: str, admin_username: str) -> bool:
        """Update user password (only callable by admin)"""
        if admin_username != "iiooooiooi":
            raise PermissionError("Only admin can update passwords")
        
        if username == "iiooooiooi":
            raise PermissionError("Use update_admin_password for admin account")
        
        try:
            password_hash = self._hash_password(new_password)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (password_hash, username))
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False
    
    def update_admin_username(self, old_username: str, new_username: str, current_password: str) -> bool:
        """Update admin username (requires current password verification)"""
        # Verify current password
        if not self.verify_user(old_username, current_password):
            raise PermissionError("Current password is incorrect")
        
        if old_username != self.ADMIN_USERNAME:
            raise PermissionError("Only the main admin can use this method")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Update username in users table only (foreign keys use user IDs, not usernames)
                cursor.execute("UPDATE users SET username = ? WHERE username = ? AND role = 'admin'", 
                             (new_username, old_username))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    # Update the class constant
                    self.ADMIN_USERNAME = new_username
                    return True
                else:
                    return False
                    
        except Exception as e:
            print(f"Error updating admin username: {e}")
            return False

    def update_user_role(self, username: str, new_role: str, admin_username: str) -> bool:
        """Update user role (only callable by admin)"""
        if admin_username != "iiooooiooi":
            raise PermissionError("Only admin can update user roles")
        
        if username == "iiooooiooi":
            raise PermissionError("Cannot change the main admin's role")
        
        if new_role not in ['user', 'admin']:
            raise ValueError("Role must be 'user' or 'admin'")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET role = ? WHERE username = ?", (new_role, username))
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False
    
    def update_admin_password(self, admin_username: str, new_password: str, current_password: str) -> bool:
        """Update admin password (requires current password verification)"""
        # Verify current password
        if not self.verify_user(admin_username, current_password):
            raise PermissionError("Current password is incorrect")
        
        if admin_username != self.ADMIN_USERNAME:
            raise PermissionError("Only the main admin can use this method")
        
        try:
            password_hash = self._hash_password(new_password)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET password_hash = ? WHERE username = ? AND role = 'admin'", 
                             (password_hash, admin_username))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating admin password: {e}")
            return False
    
    def reset_password(self, username: str, new_password: str, admin_username: str) -> bool:
        """Reset any user's password (only callable by admin)"""
        if admin_username != self.ADMIN_USERNAME:
            raise PermissionError("Only admin can reset passwords")
        
        try:
            password_hash = self._hash_password(new_password)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", 
                             (password_hash, username))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error resetting password: {e}")
            return False
    
    # Constants for compatibility
    ADMIN_USERNAME = "iiooooiooi"
    ADMIN_PASSWORD = "301415"