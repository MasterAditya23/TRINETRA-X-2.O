import sqlite3
import os

# Dynamically find the project root so it always saves in the right place
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(BASE_DIR, 'data', 'trinetra.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'backend', 'database', 'schema.sql')

def get_db_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    # This allows us to access columns by name (like dictionaries)
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    """Initializes the database using schema.sql and adds a default camera."""
    print(f"[INFO] Initializing database at {DB_PATH}...")
    
    conn = get_db_connection()
    
    # Read and execute the SQL schema
    with open(SCHEMA_PATH, 'r') as f:
        conn.executescript(f.read())
    
    # Insert a default camera for our demo (CAM-01)
    conn.execute('''
        INSERT OR IGNORE INTO cameras (camera_id, name, location, source)
        VALUES ('CAM-01', 'North Gate', 'Sector A', '0')
    ''')
    
    conn.commit()
    conn.close()
    print("[INFO] Database initialized successfully. CAM-01 is ready.")

if __name__ == '__main__':
    # When this file is run directly, it initializes the database
    init_db()