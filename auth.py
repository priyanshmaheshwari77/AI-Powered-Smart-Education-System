import sqlite3
import hashlib
import os

DB_PATH = "edu_vision.db"

def init_db():
    """Initialize SQLite tables."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Users Table
    try:
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (username TEXT PRIMARY KEY, email TEXT, password TEXT)''')
        conn.commit()
    except sqlite3.OperationalError as e:
        print(f"Warning: Could not initialize auth DB (read-only file system?): {e}")
    finally:
        conn.close()

# Initialize on import
try:
    init_db()
except Exception as e:
    print(f"Failed to run init_db on import: {e}")

def signup(username, email, password):
    """Register a new user."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Hash password using sha256
    hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    try:
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                  (username, email, hashed))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login(username, password):
    """Verify user credentials."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    
    if result:
        stored_password = result[0]
        try:
            return hashlib.sha256(password.encode('utf-8')).hexdigest() == stored_password
        except Exception:
            return False
    return False

def login_user(username, password):
    """Wrapper for UI compatibility."""
    if login(username, password):
        return True, "Login successful!"
    return False, "Invalid username or password."

def signup_user(username, password, email):
    """Wrapper for UI compatibility."""
    if signup(username, email, password):
        return True, "Account created!"
    return False, "Username already exists."

def update_password(username, new_password):
    """Update user password."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    hashed = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
    c.execute("UPDATE users SET password = ? WHERE username = ?", (hashed, username))
    conn.commit()
    rows_affected = c.rowcount
    conn.close()
    return rows_affected > 0

def get_user(username):
    """Fetch user details."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, email FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result:
        return {"username": result[0], "email": result[1]}
    return None
