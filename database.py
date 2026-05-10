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
    conn.commit()
    conn.close()

_ensure_health_table()

# ═══════════════════════════════════════════════════════════
# PHYSICIAN ALERT SYSTEM
# ═══════════════════════════════════════════════════════════
def save_physician_info(session_id, physician_email, physician_name=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS physician_alerts (
            session_id TEXT PRIMARY KEY,
            physician_email TEXT NOT NULL,
            physician_name TEXT,
            alert_enabled INTEGER DEFAULT 1,
            last_alert_sent TEXT,
            consent_given INTEGER DEFAULT 1
        )
    """)
    cursor.execute("INSERT OR REPLACE INTO physician_alerts (session_id, physician_email, physician_name) VALUES (?, ?, ?)",
                   (session_id, physician_email, physician_name))
    conn.commit()
    conn.close()

def get_physician_info(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM physician_alerts WHERE session_id=?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def generate_health_summary(session_id):
    """Generate a structured health summary for physician."""
    import datetime
    summary = []
    summary.append(f"PLOGGING LEAGUE BERLIN — HEALTH SUMMARY")
    summary.append(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    summary.append(f"Session ID: {session_id}")
    summary.append("-" * 50)
    
    # Get latest balance test
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_checkins WHERE session_id=? AND balance_sec IS NOT NULL ORDER BY timestamp DESC LIMIT 1", (session_id,))
    balance = cursor.fetchone()
    if balance:
        bal = dict(balance)
        summary.append(f"BALANCE: {bal['balance_sec']:.1f}s | {'Normal' if bal['balance_sec'] >= 10 else 'BELOW NORMAL — Fall risk'}")
    
    # Get latest reaction time
    cursor.execute("SELECT * FROM health_checkins WHERE session_id=? AND reaction_ms IS NOT NULL ORDER BY timestamp DESC LIMIT 1", (session_id,))
    reaction = cursor.fetchone()
    if reaction:
        rxn = dict(reaction)
        summary.append(f"REACTION TIME: {rxn['reaction_ms']:.0f}ms | {'Normal' if rxn['reaction_ms'] < 500 else 'SLOW — Cognitive concern'}")
    
    # Get mood trend
    cursor.execute("SELECT * FROM mood_log WHERE session_id=? ORDER BY timestamp DESC LIMIT 5", (session_id,))
    moods = cursor.fetchall()
    if moods:
        mood_list = [dict(m) for m in moods]
        avg_before = sum(m['mood_before'] for m in mood_list) / len(mood_list)
        avg_after = sum(m['mood_after'] for m in mood_list) / len(mood_list)
        summary.append(f"MOOD (avg, 1-4 scale): Before={avg_before:.1f} After={avg_after:.1f}")
        if avg_before <= 1.5:
            summary.append("⚠️ CONSISTENTLY LOW MOOD — Screen for depression")
    
    # Get condition adherence
    cursor.execute("SELECT * FROM user_conditions WHERE session_id=?", (session_id,))
    cond = cursor.fetchone()
    if cond:
        c = dict(cond)
        summary.append(f"CONDITION: {c['condition_type']} | Streak: {c['adherence_streak']} sessions")
        if c['adherence_streak'] == 0:
            summary.append("⚠️ NO RECENT ACTIVITY — Discuss barriers to exercise")
    
    conn.close()
    return "\n".join(summary)

def should_alert_physician(session_id):
    """Check if health data triggers an alert."""
    conn = get_connection()
    cursor = conn.cursor()
    alert = False
    reasons = []
    
    # Check balance
    cursor.execute("SELECT * FROM health_checkins WHERE session_id=? AND balance_sec IS NOT NULL ORDER BY timestamp DESC LIMIT 1", (session_id,))
    bal = cursor.fetchone()
    if bal and dict(bal)['balance_sec'] < 10:
        alert = True
        reasons.append("Balance below normal (fall risk)")
    
    # Check reaction time
    cursor.execute("SELECT * FROM health_checkins WHERE session_id=? AND reaction_ms IS NOT NULL ORDER BY timestamp DESC LIMIT 1", (session_id,))
    rxn = cursor.fetchone()
    if rxn and dict(rxn)['reaction_ms'] > 500:
        alert = True
        reasons.append("Slow reaction time (cognitive concern)")
    
    # Check mood
    cursor.execute("SELECT * FROM mood_log WHERE session_id=? ORDER BY timestamp DESC LIMIT 3", (session_id,))
    moods = cursor.fetchall()
    if moods:
        mood_list = [dict(m) for m in moods]
        avg = sum(m['mood_before'] for m in mood_list) / len(mood_list)
        if avg <= 1.5:
            alert = True
            reasons.append("Persistent low mood")
    
    conn.close()
    return alert, reasons
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

# ═══════════════════════════════════════════════════════════
# PHYSICIAN ALERT SYSTEM
# ═══════════════════════════════════════════════════════════
def save_physician_info(session_id, physician_email, physician_name=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS physician_alerts (
            session_id TEXT PRIMARY KEY,
            physician_email TEXT NOT NULL,
            physician_name TEXT,
            alert_enabled INTEGER DEFAULT 1,
            last_alert_sent TEXT,
            consent_given INTEGER DEFAULT 1
        )
    """)
    cursor.execute("INSERT OR REPLACE INTO physician_alerts (session_id, physician_email, physician_name) VALUES (?, ?, ?)",
                   (session_id, physician_email, physician_name))
    conn.commit()
    conn.close()

def get_physician_info(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM physician_alerts WHERE session_id=?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def generate_health_summary(session_id):
    """Generate a structured health summary for physician."""
    import datetime
    summary = []
    summary.append(f"PLOGGING LEAGUE BERLIN — HEALTH SUMMARY")
    summary.append(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    summary.append(f"Session ID: {session_id}")
    summary.append("-" * 50)
    
    # Get latest balance test
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_checkins WHERE session_id=? AND balance_sec IS NOT NULL ORDER BY timestamp DESC LIMIT 1", (session_id,))
    balance = cursor.fetchone()
    if balance:
        bal = dict(balance)
        summary.append(f"BALANCE: {bal['balance_sec']:.1f}s | {'Normal' if bal['balance_sec'] >= 10 else 'BELOW NORMAL — Fall risk'}")
    
    # Get latest reaction time
    cursor.execute("SELECT * FROM health_checkins WHERE session_id=? AND reaction_ms IS NOT NULL ORDER BY timestamp DESC LIMIT 1", (session_id,))
    reaction = cursor.fetchone()
    if reaction:
        rxn = dict(reaction)
        summary.append(f"REACTION TIME: {rxn['reaction_ms']:.0f}ms | {'Normal' if rxn['reaction_ms'] < 500 else 'SLOW — Cognitive concern'}")
    
    # Get mood trend
    cursor.execute("SELECT * FROM mood_log WHERE session_id=? ORDER BY timestamp DESC LIMIT 5", (session_id,))
    moods = cursor.fetchall()
    if moods:
        mood_list = [dict(m) for m in moods]
        avg_before = sum(m['mood_before'] for m in mood_list) / len(mood_list)
        avg_after = sum(m['mood_after'] for m in mood_list) / len(mood_list)
        summary.append(f"MOOD (avg, 1-4 scale): Before={avg_before:.1f} After={avg_after:.1f}")
        if avg_before <= 1.5:
            summary.append("⚠️ CONSISTENTLY LOW MOOD — Screen for depression")
    
    # Get condition adherence
    cursor.execute("SELECT * FROM user_conditions WHERE session_id=?", (session_id,))
    cond = cursor.fetchone()
    if cond:
        c = dict(cond)
        summary.append(f"CONDITION: {c['condition_type']} | Streak: {c['adherence_streak']} sessions")
        if c['adherence_streak'] == 0:
            summary.append("⚠️ NO RECENT ACTIVITY — Discuss barriers to exercise")
    
    conn.close()
    return "\n".join(summary)

def should_alert_physician(session_id):
    """Check if health data triggers an alert."""
    conn = get_connection()
    cursor = conn.cursor()
    alert = False
    reasons = []
    
    # Check balance
    cursor.execute("SELECT * FROM health_checkins WHERE session_id=? AND balance_sec IS NOT NULL ORDER BY timestamp DESC LIMIT 1", (session_id,))
    bal = cursor.fetchone()
    if bal and dict(bal)['balance_sec'] < 10:
        alert = True
        reasons.append("Balance below normal (fall risk)")
    
    # Check reaction time
    cursor.execute("SELECT * FROM health_checkins WHERE session_id=? AND reaction_ms IS NOT NULL ORDER BY timestamp DESC LIMIT 1", (session_id,))
    rxn = cursor.fetchone()
    if rxn and dict(rxn)['reaction_ms'] > 500:
        alert = True
        reasons.append("Slow reaction time (cognitive concern)")
    
    # Check mood
    cursor.execute("SELECT * FROM mood_log WHERE session_id=? ORDER BY timestamp DESC LIMIT 3", (session_id,))
    moods = cursor.fetchall()
    if moods:
        mood_list = [dict(m) for m in moods]
        avg = sum(m['mood_before'] for m in mood_list) / len(mood_list)
        if avg <= 1.5:
            alert = True
            reasons.append("Persistent low mood")
    
    conn.close()
    return alert, reasons
print("Database initialized: plogging_league.db")

