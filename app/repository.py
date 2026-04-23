from flask import g
from app.db import get_db

def add_highscore(name, score):
    """
    Fügt einen neuen Highscore in die SQLite-Datenbank ein.
    """
    db = get_db()
    cursor = db.cursor()
    
    query = "INSERT INTO highscore (name, score) VALUES (?, ?)"
    cursor.execute(query, (name, score))
    db.commit()
    cursor.close()

def get_top_highscores(limit=10):
    """
    Gibt die Top N Highscores aus der SQLite-Datenbank zurück.
    """
    db = get_db()
    cursor = db.cursor()
    
    # SQLite nutzt ? als Platzhalter und Row-Factory für Dict-ähnlichen Zugriff
    query = "SELECT name, score, timestamp FROM highscore ORDER BY score DESC LIMIT ?"
    cursor.execute(query, (limit,))
    
    result = cursor.fetchall()
    formatted_result = []
    
    for row in result:
        # sqlite3.Row in Dict umwandeln
        item = {
            'name': row['name'],
            'score': row['score'],
            'timestamp': row['timestamp']
        }
        formatted_result.append(item)
        
    cursor.close()
    return formatted_result
