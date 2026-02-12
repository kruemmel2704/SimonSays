import json
import os
from flask import Blueprint, render_template
from app.config import HIGHSCORE_FILE

# Blueprint definieren
main_bp = Blueprint('main', __name__)

def get_highscores():
    """Hilfsfunktion zum Laden der Highscores."""
    if not os.path.exists(HIGHSCORE_FILE):
        return []
    
    try:
        with open(HIGHSCORE_FILE, 'r') as f:
            scores = json.load(f)
            # Sortieren nach Punktzahl (höchste zuerst)
            return sorted(scores, key=lambda x: x['score'], reverse=True)[:10]
    except (json.JSONDecodeError, IOError):
        return []

@main_bp.route('/')
def dashboard():
    """Die Hauptseite mit den Highscores."""
    scores = get_highscores()
    return render_template('dashboard.html', scores=scores)

@main_bp.route('/remote')
def remote():
    """Die Seite für die Echtzeit-Fernsteuerung/Anzeige."""
    from app.config import DIFFICULTY_SETTINGS
    return render_template('remote.html', difficulty_settings=DIFFICULTY_SETTINGS)