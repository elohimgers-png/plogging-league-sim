# database.py — SQLite Database for Plogging League
import sqlite3
import datetime
import os

DB_PATH = "plogging_league.db"

def get_connection():
    """Create or connect to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Teams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            color TEXT NOT NULL,
            total_points INTEGER DEFAULT 0,
            total_collected INTEGER DEFAULT 0,
            total_distance REAL DEFAULT 0.0,
            games_played INTEGER DEFAULT 0
        )
    ''')
    
    # Sessions table (each simulation run)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT NOT NULL,
            points INTEGER DEFAULT 0,
            collected INTEGER DEFAULT 0,
            distance REAL DEFAULT 0.0,
            clean_score REAL DEFAULT 0.0,
            day INTEGER DEFAULT 0,
            hour INTEGER DEFAULT 0,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Global stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS global_stats (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            total_litter_collected INTEGER DEFAULT 0,
            total_distance REAL DEFAULT 0.0,
            total_cp_earned INTEGER DEFAULT 0,
            total_sessions INTEGER DEFAULT 0,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default teams if empty
    default_teams = [
        ("Red Rangers", "#ff0000"),
        ("Green Guardians", "#00cc00"),
        ("Black Knights", "#999999"),
        ("Yellow Storm", "#ffdd00"),
    ]
    
    for name, color in default_teams:
        cursor.execute('''
            INSERT OR IGNORE INTO teams (name, color) VALUES (?, ?)
        ''', (name, color))
    
    # Insert global stats row if not exists
    cursor.execute('''
        INSERT OR IGNORE INTO global_stats (id) VALUES (1)
    ''')
    
    conn.commit()
    conn.close()

def save_session(team_name, points, collected, distance, clean_score, day, hour):
    """Save a completed plogging session."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Insert session record
    cursor.execute('''
        INSERT INTO sessions (team_name, points, collected, distance, clean_score, day, hour)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (team_name, points, collected, distance, clean_score, day, hour))
    
    # Update team totals
    cursor.execute('''
        UPDATE teams 
        SET total_points = total_points + ?,
            total_collected = total_collected + ?,
            total_distance = total_distance + ?,
            games_played = games_played + 1
        WHERE name = ?
    ''', (points, collected, distance, team_name))
    
    # Update global stats
    cursor.execute('''
        UPDATE global_stats
        SET total_litter_collected = total_litter_collected + ?,
            total_distance = total_distance + ?,
            total_cp_earned = total_cp_earned + ?,
            total_sessions = total_sessions + 1,
            last_updated = CURRENT_TIMESTAMP
        WHERE id = 1
    ''', (collected, distance, points))
    
    conn.commit()
    conn.close()

def get_leaderboard():
    """Get all-time team leaderboard."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name, color, total_points, total_collected, total_distance, games_played FROM teams ORDER BY total_points DESC')
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

def get_global_stats():
    """Get global cumulative stats."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM global_stats WHERE id = 1')
    result = dict(cursor.fetchone())
    conn.close()
    return result

def get_recent_sessions(limit=10):
    """Get most recent sessions."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sessions ORDER BY timestamp DESC LIMIT ?', (limit,))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

def save_health_checkin(session_id, balance_sec=None, flexibility_cm=None, reaction_ms=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO health_checkins (session_id, balance_sec, flexibility_cm, reaction_ms)
        VALUES (?, ?, ?, ?)
    ''', (session_id, balance_sec, flexibility_cm, reaction_ms))
    conn.commit()
    conn.close()

def save_mood(session_id, mood_before, mood_after, notes=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO mood_log (session_id, mood_before, mood_after, notes) VALUES (?, ?, ?, ?)",
                   (session_id, mood_before, mood_after, notes))
    conn.commit()
    conn.close()

def get_mood_trends(session_id, limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mood_log WHERE session_id=? ORDER BY timestamp DESC LIMIT ?", (session_id, limit))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

def save_user_condition(session_id, condition_type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO user_conditions (session_id, condition_type, regimen_start) VALUES (?, ?, CURRENT_TIMESTAMP)",
                   (session_id, condition_type))
    conn.commit()
    conn.close()

def get_user_condition(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_conditions WHERE session_id=?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_adherence(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_conditions SET adherence_streak = adherence_streak + 1, last_session = CURRENT_TIMESTAMP WHERE session_id=?", (session_id,))
    conn.commit()
    conn.close()

def get_health_trends(session_id, limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM health_checkins 
        WHERE session_id=? 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (session_id, limit))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

# Initialize database on import
init_db()

# Force health_checkins table creation (idempotent)
def _ensure_health_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            balance_sec REAL,
            flexibility_cm REAL,
            reaction_ms REAL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            mood_before INTEGER,
            mood_after INTEGER,
            notes TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_conditions (
            session_id TEXT PRIMARY KEY,
            condition_type TEXT NOT NULL,
            regimen_start TEXT DEFAULT CURRENT_TIMESTAMP,
            adherence_streak INTEGER DEFAULT 0,
            last_session TEXT
        )
    """)
    conn.commit()
    conn.close()

_ensure_health_table()
print("Database initialized: plogging_league.db")

