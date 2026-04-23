from flask import Flask, g
import os
import sys

# Mock current_app configuration
class MockApp:
    def __init__(self):
        self.config = {
            'MYSQL_HOST': 'localhost',
            'MYSQL_USER': 'simon',
            'MYSQL_PASSWORD': 'simon123',
            'MYSQL_DB': 'simon_says'
        }
        self.root_path = os.getcwd()

app = Flask(__name__)
app.config.update({
    'MYSQL_HOST': 'localhost',
    'MYSQL_USER': 'simon',
    'MYSQL_PASSWORD': 'simon123',
    'MYSQL_DB': 'simon_says'
})

# Mocking the context for testing db.py
sys.path.append(os.getcwd())
import app.db as db

with app.app_context():
    print("Testing init_db...")
    try:
        db.init_db()
        print("init_db finished.")
        print(f"DB Type: {g.get('db_type')}")
    except Exception as e:
        print(f"Error in init_db: {e}")

    print("\nTesting get_db...")
    try:
        conn = db.get_db()
        print(f"get_db returned: {conn}")
    except Exception as e:
        print(f"Error in get_db: {e}")
