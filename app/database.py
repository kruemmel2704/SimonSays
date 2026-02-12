# app/database.py
import mysql.connector
from mysql.connector import Error
from flask import g
from app.config import DB_CONFIG
import logging

logger = logging.getLogger(__name__)

def get_db():
    """Datenbankverbindung für den aktuellen Request holen."""
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(
                host=DB_CONFIG['host'],
                database=DB_CONFIG['database'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                port=DB_CONFIG['port']
            )
        except Error as e:
            logger.error(f"Datenbankverbindung fehlgeschlagen: {e}")
            raise
    return g.db

def close_db(e=None):
    """Datenbankverbindung schließen."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Datenbanktabellen erstellen falls nicht vorhanden."""
    db = get_db()
    cursor = db.cursor()
    
    # Tabelle für Spieler
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabelle für Highscores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS highscores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            player_id INT NOT NULL,
            score INT NOT NULL,
            difficulty VARCHAR(20) DEFAULT 'medium',
            achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES players(id),
            INDEX idx_score (score DESC),
            INDEX idx_achieved (achieved_at DESC)
        )
    """)
    
    db.commit()
    cursor.close()
    logger.info("Datenbank-Tabellen wurden initialisiert")

def save_player(player_name):
    """Neuen Spieler speichern oder existierenden zurückgeben."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Prüfen ob Spieler existiert
    cursor.execute("SELECT id FROM players WHERE name = %s", (player_name,))
    player = cursor.fetchone()
    
    if player:
        player_id = player['id']
    else:
        # Neuen Spieler anlegen
        cursor.execute("INSERT INTO players (name) VALUES (%s)", (player_name,))
        db.commit()
        player_id = cursor.lastrowid
    
    cursor.close()
    return player_id

def save_score(player_id, score, difficulty='medium'):
    """Highscore speichern."""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        INSERT INTO highscores (player_id, score, difficulty)
        VALUES (%s, %s, %s)
    """, (player_id, score, difficulty))
    
    db.commit()
    cursor.close()

def get_top_highscores(limit=10):
    """Top Highscores mit Spielernamen laden."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT p.name, h.score, h.difficulty, h.achieved_at
        FROM highscores h
        JOIN players p ON h.player_id = p.id
        ORDER BY h.score DESC, h.achieved_at ASC
        LIMIT %s
    """, (limit,))
    
    scores = cursor.fetchall()
    cursor.close()
    return scores

def get_player_scores(player_name, limit=5):
    """Highscores eines bestimmten Spielers laden."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT p.name, h.score, h.difficulty, h.achieved_at
        FROM highscores h
        JOIN players p ON h.player_id = p.id
        WHERE p.name = %s
        ORDER BY h.score DESC
        LIMIT %s
    """, (player_name, limit))
    
    scores = cursor.fetchall()
    cursor.close()
    return scores