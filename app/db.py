import os
import sqlite3

from flask import current_app, g

try:
    import mysql.connector
except ImportError:
    mysql = None

def get_db():
    if 'db' not in g:
        # Versuch MySQL zu verbinden
        try:
            if mysql is None:
                raise ImportError("mysql-connector-python ist nicht installiert")
            g.db = mysql.connector.connect(
                host=current_app.config['MYSQL_HOST'],
                user=current_app.config['MYSQL_USER'],
                password=current_app.config['MYSQL_PASSWORD'],
                database=current_app.config['MYSQL_DB'],
                connect_timeout=2 # Kurz halten für Fallback
            )
            print("MySQL Verbindung erfolgreich.")
            g.db_type = 'mysql'
        except Exception as e:
            print(f"MySQL Verbindung fehlgeschlagen ({e}). Fallback auf SQLite...")
            # Fallback auf SQLite
            db_path = os.path.join(current_app.root_path, '..', 'simon.db')
            g.db = sqlite3.connect(db_path)
            g.db.row_factory = sqlite3.Row # Dictionaries simulieren
            g.db_type = 'sqlite'
            
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database table."""
    db = get_db()
    cursor = db.cursor()
    
    if g.get('db_type') == 'mysql':
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS highscore (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                score INT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
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
