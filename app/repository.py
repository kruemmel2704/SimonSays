
from app.db import get_db

def add_highscore(name, score):
    """
    Fügt einen neuen Highscore in die Datenbank ein.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO highscore (name, score) VALUES (%s, %s)",
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
    cursor = db.cursor(dictionary=True) # WICHTIG für MySQL: Gibt Dictionaries statt Tuples zurück
    cursor.execute(
        "SELECT * FROM highscore ORDER BY score DESC LIMIT %s",
        (limit,)
    )
    result = cursor.fetchall()
    
    formatted_result = []
    for row in result:
        # Falls timestamp ein datetime Objekt ist, in ISO-Format umwandeln
        if 'timestamp' in row and row['timestamp'] and hasattr(row['timestamp'], 'isoformat'):
             row['timestamp'] = row['timestamp'].isoformat()
        formatted_result.append(row)
        
    cursor.close()
    return formatted_result
