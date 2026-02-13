
import sys
import os

# Add the project root directory to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db import get_db, init_db
from flask import Flask

app = Flask(__name__)
# Configure for testing
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'simon'
app.config['MYSQL_PASSWORD'] = 'simon123'
app.config['MYSQL_DB'] = 'simon_says'

# Or read from config file
# app.config.from_object('app.config')

print("Testing Database Connection...")

try:
    with app.app_context():
        # Try to initialize DB (create table)
        print("Initializing DB...")
        init_db()
        print("DB Initialized.")
        
        # Try to insert a dummy record
        from app.repository import add_highscore, get_top_highscores
        
        print("Adding Highscore...")
        add_highscore("TestBot", 999)
        
        print("Reading Highscores...")
        scores = get_top_highscores()
        print(f"Highscores: {scores}")
        
        found = False
        for s in scores:
            if s['name'] == 'TestBot' and s['score'] == 999:
                found = True
                break
        
        if found:
            print("SUCCESS: TestBot found in highscores.")
        else:
            print("FAILURE: TestBot not found.")
            sys.exit(1)

except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
