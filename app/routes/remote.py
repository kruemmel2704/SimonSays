from flask import Blueprint
from flask_socketio import emit
from app import socketio, game_instance

# Blueprint für die Remote-Routen
remote_bp = Blueprint('remote', __name__)

@socketio.on('connect', namespace='/remote')
def handle_connect():
    """Wird aufgerufen, wenn ein Benutzer das Remote-Interface öffnet."""
    print("Client verbunden mit /remote")
    emit('status', {'msg': 'Verbunden mit SimonSays Remote'})

@socketio.on('change_difficulty', namespace='/remote')
def handle_difficulty(data):
    """
    Ändert den Schwierigkeitsgrad zur Laufzeit.
    Erwartet data: {'level': 'easy' | 'medium' | 'hard'}
    """
    level = data.get('level')
    from app.config import DIFFICULTY_SETTINGS
    
    if level in DIFFICULTY_SETTINGS:
        settings = DIFFICULTY_SETTINGS[level]
        # Wir ändern die Werte direkt in der laufenden Spielinstanz
        game_instance.flash_delay = settings['flash']
        game_instance.sequence_pause = settings['pause']
        
        print(f"Schwierigkeit geändert auf: {level}")
        emit('difficulty_changed', {'level': level}, broadcast=True, namespace='/remote')

@socketio.on('remote_input', namespace='/remote')
def handle_remote_input(data):
    """
    Ermöglicht es, das Spiel über die Website zu steuern.
    Erwartet data: {'color': 'red' | 'green' | ...}
    """
    color = data.get('color')
    print(f"Remote-Klick erkannt: {color}")
    
    # Hier könnte man eine Logik einbauen, um den physischen Tastendruck 
    # durch einen virtuellen zu ersetzen/ergänzen.
    emit('remote_feedback', {'color': color}, broadcast=True, namespace='/remote')

@socketio.on('web_button_press', namespace='/remote')
def handle_web_press(data):
    color = data.get('color')
    print(f"Web-Klick empfangen: {color}")
    if game_instance:
        # Wir simulieren für die Spiellogik einen Tastendruck
        game_instance.handle_web_input(color)