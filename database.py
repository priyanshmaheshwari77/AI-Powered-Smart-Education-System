import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "edu_vision.db"

def init_history_db():
    """Initialize history table in SQLite."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT, 
                  topic TEXT, 
                  full_content TEXT, 
                  timestamp DATETIME)''')
    conn.commit()
    conn.close()

# Initialize on import
init_history_db()

def save_chat_history(username, topic, full_content):
    """Save learning history to SQLite."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    content_json = json.dumps(full_content)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO history (username, topic, full_content, timestamp) VALUES (?, ?, ?, ?)", 
              (username, topic, content_json, timestamp))
    conn.commit()
    conn.close()

def get_user_history(username):
    """Retrieve all history for a specific user."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT topic, full_content, timestamp, id FROM history WHERE username = ? ORDER BY timestamp DESC", (username,))
    rows = c.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "topic": row[0],
            "full_content": json.loads(row[1]),
            "timestamp": row[2],
            "_id": row[3]
        })
    return history

def save_to_knowledge_base(topic, content):
    """Disabled - no longer using vector DB for speed."""
    return True

def search_knowledge_base(query):
    """Disabled - no longer using vector DB for speed."""
    return None

def get_user(username):
    """Fetch user (re-export from auth for compatibility)."""
    import auth
    return auth.get_user(username)
