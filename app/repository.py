from flask import g
from app.db import get_db

def add_highscore(name, score):
    """
    Fügt einen neuen Highscore in die Datenbank ein.
    """
    db = get_db()
    cursor = db.cursor()
    
    placeholder = "%s" if g.get('db_type') == 'mysql' else "?"
    query = f"INSERT INTO highscore (name, score) VALUES ({placeholder}, {placeholder})"
    
    cursor.execute(query, (name, score))
    db.commit()
    cursor.close()

def get_top_highscores(limit=10):
    """
    Gibt die Top N Highscores zurück.
    """
    db = get_db()
    
    # Cursor-Verhalten unterscheidet sich
    if g.get('db_type') == 'mysql':
        cursor = db.cursor(dictionary=True)
        placeholder = "%s"
    else:
        cursor = db.cursor()
        placeholder = "?"
        
    query = f"SELECT name, score, timestamp FROM highscore ORDER BY score DESC LIMIT {placeholder}"
    cursor.execute(query, (limit,))
    
    result = cursor.fetchall()
    formatted_result = []
    
    for row in result:
        # SQLite Row in Dict umwandeln
        if g.get('db_type') == 'sqlite':
            item = {
                'name': row[0],
                'score': row[1],
                'timestamp': row[2]
            }
        else:
            item = row
            
        # Timestamp-Formatierung
        if 'timestamp' in item and item['timestamp'] and hasattr(item['timestamp'], 'isoformat'):
             item['timestamp'] = item['timestamp'].isoformat()
        formatted_result.append(item)
        
    cursor.close()
    return formatted_result
