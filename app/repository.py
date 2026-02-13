
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
    cursor = db.cursor(dictionary=True) # Ensure we get dicts
    cursor.execute(
        "SELECT * FROM highscore ORDER BY score DESC LIMIT %s",
        (limit,)
    )
    result = cursor.fetchall()
    
    # Check if we need to format timestamp? 
    # Usually mysql-connector returns datetime objects.
    # Our previous to_dict() method formatted it to isoformat.
    
    formatted_result = []
    for row in result:
        # Convert datetime to isoformat string if it's there
        if 'timestamp' in row:
             row['timestamp'] = row['timestamp'].isoformat()
        formatted_result.append(row)
        
    cursor.close()
    return formatted_result
