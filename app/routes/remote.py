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
    """
    level = data.get('level')
    from app.config import DIFFICULTY_SETTINGS
    
    if level in DIFFICULTY_SETTINGS:
        settings = DIFFICULTY_SETTINGS[level]
        # Wir ändern die Werte direkt in der laufenden Spielinstanz
        if game_instance:
            game_instance.flash_delay = settings['flash']
            game_instance.sequence_pause = settings['pause']
        
        print(f"Schwierigkeit geändert auf: {level}")
        emit('difficulty_changed', {'level': level}, broadcast=True, namespace='/remote')

@socketio.on('remote_input', namespace='/remote')
def handle_remote_input(data):
    """
    Hier kommt der Klick aus der HTML an (remote_input).
    Wir müssen:
    1. Feedback an alle Browser senden (damit es überall blinkt).
    2. Die Spiel-Logik informieren (damit das Spiel weitergeht).
    """
    color = data.get('color')
    print(f"Web-Input empfangen: {color}")
    
    # 1. Visuelles Feedback an alle verbundenen Clients (Synchronisation)
    emit('led_state', {'color': color, 'state': 'on'}, broadcast=True, namespace='/remote')
    # Kurze Pause simulieren wir im Browser per JS Timeout, 
    # hier senden wir nur das Signal "Es wurde gedrückt".
    
    # 2. Spiel-Logik informieren (DAS FEHLTE VORHER AN DIESER STELLE)
    if game_instance:
        game_instance.process_remote_input(color)