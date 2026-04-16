
from app.db import get_db

def add_highscore(name, score):
    """
    Fügt einen neuen Highscore in die Datenbank ein.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO highscore (name, score) VALUES (?, ?)",
        (name, score)
    )
    db.commit()
    cursor.close()

def get_top_highscores(limit=10):
    """
    Gibt die Top N Highscores zurück.
    Format: Liste von Dictionaries mit 'name', 'score', 'timestamp'
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM highscore ORDER BY score DESC LIMIT ?",
        (limit,)
    )
    result = cursor.fetchall()
    
    formatted_result = []
    for row in result:
        # sqlite3.Row objects behave like dicts, but let's convert to real dict for JSON safety
        d = dict(row)
        # Check if timestamp is a string (SQLite often returns strings for dates)
        # and ensure it's in a consistent format
        if 'timestamp' in d and d['timestamp'] and hasattr(d['timestamp'], 'isoformat'):
             d['timestamp'] = d['timestamp'].isoformat()
        
        formatted_result.append(d)
        
    cursor.close()
    return formatted_result
