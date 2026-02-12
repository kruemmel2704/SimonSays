# app/main.py
import json
import os
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, g
from app.config import HIGHSCORE_FILE
from app.database import get_top_highscores, save_player, close_db, init_db
import logging

logger = logging.getLogger(__name__)

# Blueprint definieren
main_bp = Blueprint('main', __name__)

@main_bp.before_app_request
def before_request():
    """Vor jedem Request die Datenbankverbindung herstellen."""
    if 'db' not in g:
        try:
            init_db()
        except Exception as e:
            logger.error(f"Datenbank-Initialisierung fehlgeschlagen: {e}")

@main_bp.teardown_app_request
def teardown_db(e=None):
    """Nach jedem Request die Datenbankverbindung schließen."""
    close_db(e)

def get_highscores():
    """Hilfsfunktion zum Laden der Highscores (Fallback für JSON)."""
    if not os.path.exists(HIGHSCORE_FILE):
        return []
    
    try:
        with open(HIGHSCORE_FILE, 'r') as f:
            scores = json.load(f)
            return sorted(scores, key=lambda x: x['score'], reverse=True)[:10]
    except (json.JSONDecodeError, IOError):
        return []

@main_bp.route('/')
def dashboard():
    """Die Hauptseite mit den Highscores."""
    try:
        # Versuche Highscores aus der Datenbank zu laden
        scores = get_top_highscores()
    except Exception as e:
        logger.error(f"Fehler beim Laden der Highscores: {e}")
        # Fallback: JSON-Datei
        scores = get_highscores()
    
    # Prüfen ob Spielername in Session existiert
    player_name = session.get('player_name', '')
    
    return render_template('dashboard.html', scores=scores, current_player=player_name)

@main_bp.route('/remote')
def remote():
    """Die Seite für die Echtzeit-Fernsteuerung/Anzeige."""
    player_name = session.get('player_name', '')
    if not player_name:
        flash('Bitte geben Sie zuerst einen Spielernamen ein.', 'warning')
        return redirect(url_for('main.dashboard'))
    return render_template('remote.html', player_name=player_name)

@main_bp.route('/set_player', methods=['POST'])
def set_player():
    """Spielername setzen."""
    player_name = request.form.get('player_name', '').strip()
    
    if player_name:
        if len(player_name) < 3:
            flash('Spielername muss mindestens 3 Zeichen lang sein.', 'error')
        elif len(player_name) > 50:
            flash('Spielername darf maximal 50 Zeichen lang sein.', 'error')
        else:
            try:
                # Spieler in Datenbank speichern
                player_id = save_player(player_name)
                session['player_id'] = player_id
                session['player_name'] = player_name
                flash(f'Willkommen, {player_name}!', 'success')
                logger.info(f"Spieler {player_name} (ID: {player_id}) angemeldet")
            except Exception as e:
                logger.error(f"Fehler beim Speichern des Spielers: {e}")
                flash('Fehler beim Speichern des Spielernamens.', 'error')
    else:
        flash('Bitte geben Sie einen Spielernamen ein.', 'error')
    
    return redirect(url_for('main.dashboard'))

@main_bp.route('/logout')
def logout():
    """Spieler abmelden."""
    player_name = session.pop('player_name', None)
    session.pop('player_id', None)
    if player_name:
        flash(f'Auf Wiedersehen, {player_name}!', 'info')
    return redirect(url_for('main.dashboard'))