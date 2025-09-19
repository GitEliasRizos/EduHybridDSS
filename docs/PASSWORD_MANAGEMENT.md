# Password Management Quick Reference

## How to Change User Passwords in PyMOO GUI

### 🖥️ GUI Method (Easiest)

1. **Launch Application**: `python main.py`
2. **Login as Admin**: `iiooooiooi` / `301415`
3. **Open User Management**: Admin menu → User Management

#### For Regular Users:
- Click blue **"Reset"** button next to username
- Enter new password
- Click OK

#### For System Admin:
- Click green **"Edit Profile"** button
- Enter current password
- Enter new password
- Click "Save Changes"

### 💻 Script Method

Run the interactive script:
```bash
python change_passwords.py
```

Choose option 1 for single user, option 2 for bulk reset.

### 🐍 Programmatic Method

```python
from core.user_manager import UserDatabaseManager

user_manager = UserDatabaseManager()

# Reset regular user password
success = user_manager.reset_password(
    username="Elias",
    new_password="newpassword123",
    admin_username="iiooooiooi"
)

# Change admin password
success = user_manager.update_admin_password(
    admin_username="iiooooiooi",
    new_password="newadminpass",
    current_password="301415"
)
```

### 🔐 Security Notes

- ✅ System Admin password changes require current password
- ✅ Only admin can reset other users' passwords
- ✅ Minimum 3 characters password length
- ✅ All passwords are hashed with SHA-256
- ✅ Database transactions ensure integrity

### 📋 Current Users

Run this to see current users:
```python
from core.user_manager import UserDatabaseManager
users = UserDatabaseManager().get_all_users()
for user in users:
    print(f"{user['username']} ({user['role']})")
```