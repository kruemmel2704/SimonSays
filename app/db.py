import os
import sqlite3
from flask import current_app, g

def get_db():
    """Initialisiert die Verbindung zur SQLite-Datenbank."""
    if 'db' not in g:
        db_path = os.path.join(current_app.root_path, '..', 'simon.db')
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db_type = 'sqlite'
    return g.db

def close_db(e=None):
    """Schließt die Datenbank-Verbindung am Ende des Requests."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Erstellt die Tabellen, falls sie noch nicht existieren."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS highscore (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
    cursor.close()

def init_app(app):
    """Registriert DB-Funktionen bei der Flask-App."""
    app.teardown_appcontext(close_db)
