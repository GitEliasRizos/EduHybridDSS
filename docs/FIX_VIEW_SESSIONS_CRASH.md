# Fix Summary: "View Active Sessions" Crash Resolution

## Problem
The "View Active Sessions" menu item in the admin interface was crashing the program with the error:
```
sqlite3.OperationalError: no such column: s.optimization_results
```

## Root Cause
The database schema had been updated in the code to include new columns (`optimization_results` and `alternatives_data`) in the sessions table, but the existing database file did not have these columns. This caused a mismatch between the expected schema and the actual database structure.

## Solution

### 1. Database Migration System
Added a migration method to the `UserDatabaseManager` class:

```python
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
            cursor.execute("ALTER TABLE sessions ADD COLUMN optimization_results TEXT")
        
        # Add alternatives_data column if it doesn't exist
        if 'alternatives_data' not in column_names:
            cursor.execute("ALTER TABLE sessions ADD COLUMN alternatives_data TEXT")
        
        conn.commit()
```

### 2. Migration Integration
Updated the `UserDatabaseManager` constructor to automatically run migrations:

```python
def __init__(self, db_path: str = "databases/pymoo.db"):
    """Initialize database manager"""
    self.db_path = db_path
    self.current_session = None
    self._init_database()
    self._migrate_database()  # Apply any schema updates
    self._create_default_admin()
```

### 3. Error Handling Enhancement
Added comprehensive error handling to the `view_group_sessions` method:

```python
def view_group_sessions(self):
    """View and manage active group decision sessions"""
    try:
        # ... existing code ...
    except Exception as e:
        QMessageBox.critical(
            self, 
            "Error Loading Sessions",
            f"Failed to load group decision sessions:\n\n{str(e)}\n\n"
            "This might be due to a database issue. Please check if the database is properly initialized."
        )
```

## Database Schema Changes
The migration adds two new columns to the `sessions` table:

- `optimization_results TEXT` - Stores JSON serialized optimization results from PyMOO
- `alternatives_data TEXT` - Stores JSON array of alternatives for decision making

## Testing
1. ✅ Database migration runs successfully on first load
2. ✅ New columns are added without data loss
3. ✅ `get_active_sessions()` method works correctly
4. ✅ "View Active Sessions" menu loads without crashing
5. ✅ Test session creation and retrieval works

## Result
The admin interface now works correctly and displays active group decision sessions. The migration system ensures that existing databases are automatically updated to the latest schema without manual intervention.

## Files Modified
- `core/user_manager.py` - Added migration method and updated constructor
- `ui/main_window.py` - Enhanced error handling in view_group_sessions method

## Database Schema Version
- **Before**: Sessions table with 8 columns (id, session_name, problem_name, criteria_names, objectives_info, created_by, created_at, is_active)
- **After**: Sessions table with 10 columns (added optimization_results, alternatives_data)

The fix ensures backward compatibility and forward migration path for the database schema.