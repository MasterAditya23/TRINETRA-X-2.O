-- Table to store configured cameras
CREATE TABLE IF NOT EXISTS cameras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    location TEXT,
    source TEXT NOT NULL,
    status TEXT DEFAULT 'ONLINE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to store intrusion events
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT UNIQUE NOT NULL,
    camera_id TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    event_type TEXT NOT NULL,
    object_type TEXT NOT NULL,
    confidence REAL,
    zone TEXT,
    snapshot_path TEXT,
    status TEXT DEFAULT 'NEW',
    FOREIGN KEY (camera_id) REFERENCES cameras (camera_id)
);