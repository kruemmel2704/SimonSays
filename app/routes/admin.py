from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import app

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def is_logged_in():
    return session.get('admin_logged_in')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'admin':
            session['admin_logged_in'] = True
            return redirect(url_for('admin.debug'))
        else:
            flash('Ungültige Anmeldedaten', 'error')
            
    return render_template('admin_login.html')

@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))

@admin_bp.route('/debug')
def debug():
    if not is_logged_in():
        return redirect(url_for('admin.login'))
    
    status = {}
    if app.game_instance:
        status = app.game_instance.get_debug_status()
        
    return render_template('admin_debug.html', status=status)

@admin_bp.route('/toggle/<color>')
def toggle_led(color):
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    
    if app.game_instance:
        new_state = app.game_instance.toggle_led_debug(color)
        return jsonify({'success': True, 'color': color, 'state': 'on' if new_state else 'off'})
    
    return jsonify({'error': 'Game instance not running'}), 500

@admin_bp.route('/status')
def status_json():
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
        
    if app.game_instance:
        return jsonify(app.game_instance.get_debug_status())
    
    return jsonify({'error': 'Game instance not running'}), 500
