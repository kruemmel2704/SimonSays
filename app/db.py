
import sqlite3
from flask import current_app, g
import os

def get_db():
    if 'db' not in g:
        # Get database path from config
        db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
        if not db_path:
            # Fallback
            db_path = os.path.join(current_app.root_path, 'simon.db')
            
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row  # This allows accessing columns by name
    
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    """Initializes the database table."""
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
    app.teardown_appcontext(close_db)
