with open("database.py", "r") as f:
    content = f.read()

# Add the mood_log table creation right after the health_checkins table
old_table = '''        CREATE TABLE IF NOT EXISTS health_checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            balance_sec REAL,
            flexibility_cm REAL,
            reaction_ms REAL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)'''

new_table = '''        CREATE TABLE IF NOT EXISTS health_checkins (
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
    """)'''

content = content.replace(old_table, new_table)

# Add save_mood and get_mood_trends functions at the end
old_end = '''def get_health_trends(session_id, limit=10):
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
    return results'''

new_end = '''def get_health_trends(session_id, limit=10):
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

def save_mood(session_id, mood_before, mood_after, notes=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO mood_log (session_id, mood_before, mood_after, notes)
        VALUES (?, ?, ?, ?)
    ''', (session_id, mood_before, mood_after, notes))
    conn.commit()
    conn.close()

def get_mood_trends(session_id, limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM mood_log 
        WHERE session_id=? 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (session_id, limit))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results'''

content = content.replace(old_end, new_end)

with open("database.py", "w") as f:
    f.write(content)
print("Mood table and functions added to database.py!")
