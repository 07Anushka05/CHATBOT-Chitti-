import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime

DB_FILE = "chatbot.db"

def init_db():
    """Initialize database with required tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Chat sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_id TEXT UNIQUE NOT NULL,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    
    # Chat messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password):
    """Register a new user"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        conn.close()
        return True, "Registration successful!"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already exists!"
        elif "email" in str(e):
            return False, "Email already exists!"
        return False, "Registration failed!"
    except Exception as e:
        return False, str(e)

def login_user(username, password):
    """Authenticate user and return user_id"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return True, result[0]
        return False, "Invalid username or password"
    except Exception as e:
        return False, str(e)

def get_user_info(user_id):
    """Get user information"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT username, email, created_at FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        return None

def create_chat_session(user_id, session_id, title=""):
    """Create a new chat session"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        if not title:
            title = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        cursor.execute(
            "INSERT INTO chat_sessions (user_id, session_id, title) VALUES (?, ?, ?)",
            (user_id, session_id, title)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False

def save_message(session_id, role, content):
    """Save a message to the database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Get session database id
        cursor.execute("SELECT id FROM chat_sessions WHERE session_id = ?", (session_id,))
        result = cursor.fetchone()
        
        if result:
            session_db_id = result[0]
            cursor.execute(
                "INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)",
                (session_db_id, role, content)
            )
            # Update session's updated_at
            cursor.execute(
                "UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (session_db_id,)
            )
            conn.commit()
        
        conn.close()
        return True
    except Exception as e:
        return False

def get_user_sessions(user_id):
    """Get all chat sessions for a user"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT session_id, title, created_at, updated_at 
               FROM chat_sessions 
               WHERE user_id = ? 
               ORDER BY updated_at DESC""",
            (user_id,)
        )
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        return []

def get_session_messages(session_id):
    """Get all messages for a specific session"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT role, content 
               FROM chat_messages 
               WHERE session_id IN (SELECT id FROM chat_sessions WHERE session_id = ?)
               ORDER BY created_at ASC""",
            (session_id,)
        )
        results = cursor.fetchall()
        conn.close()
        
        # Convert to message format
        messages = [{"role": role, "content": content} for role, content in results]
        return messages
    except Exception as e:
        return []

def delete_session(session_id):
    """Delete a chat session"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False

def update_session_title(session_id, title):
    """Update session title"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE chat_sessions SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE session_id = ?",
            (title, session_id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False

# Initialize database when module is loaded
init_db()
