
import mysql.connector
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
        g.db.row_factory = sqlite3_row_factory_equivalent # mysql connector doesn't have this exactly, but we return dicts in repo usually.
        # Actually, for mysql-connector, we get cursors.
    
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    """Initializes the database table."""
    db = get_db()
    cursor = db.cursor()
    
    # Create database if it doesn't exist? 
    # Usually the DB should exist, but the table might not.
    # We can't create the DB from within the connection to the DB itself easily if it doesn't exist.
    # We assume the DB 'simon_says' exists.
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS highscore (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            score INT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
    cursor.close()

def init_app(app):
    app.teardown_appcontext(close_db)
