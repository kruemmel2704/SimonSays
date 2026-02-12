import json
from flask import Blueprint, render_template
from app import db, socketio
from app.models import Highscore
from flask_socketio import emit

# Blueprint definieren
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    """Die Hauptseite mit den Highscores."""
    # Top 10 Highscores aus der DB laden
    scores = Highscore.query.order_by(Highscore.score.desc()).limit(10).all()
    return render_template('dashboard.html', scores=scores)

@main_bp.route('/remote')
def remote():
    """Die Seite für die Echtzeit-Fernsteuerung/Anzeige."""
    from app.config import DIFFICULTY_SETTINGS
    return render_template('remote.html', difficulty_settings=DIFFICULTY_SETTINGS)

# --- SocketIO Event Handler für Highscores ---

@socketio.on('submit_highscore')
def handle_submit_highscore(data):
    """
    Wird vom Dashboard gesendet, wenn der Nutzer einen Namen eingibt.
    Format: {'name': 'Lars'}
    """
    name = data.get('name')
    if not name:
        return

    import app
    # Wir brauchen den Score vom aktuellen Spiel
    # Da gpio_logic den Score kennt, holen wir ihn von dort oder
    # wir speichern ihn temporär.
    # Besser: gpio_logic wartet auf diesen Event.
    
    if app.game_instance:
        app.game_instance.on_name_submitted(name)

@socketio.on('request_highscores')
def handle_request_highscores():
    scores = Highscore.query.order_by(Highscore.score.desc()).limit(10).all()
    # Serialize
    scores_list = [s.to_dict() for s in scores]
    emit('update_highscores', scores_list)