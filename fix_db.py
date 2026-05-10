with open("database.py", "r") as f:
    content = f.read()

old = "# Initialize database on import\ninit_db()"

new = '''# Initialize database on import
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

_ensure_health_table()'''

content = content.replace(old, new)

with open("database.py", "w") as f:
    f.write(content)
print("Done! health_checkins table forced on import.")
