from flask import Flask, jsonify, request
from flask_cors import CORS
import uuid
from datetime import datetime
from database.db import get_db_connection

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    db_status = "disconnected"
    try:
        conn = get_db_connection()
        conn.close()
        db_status = "online"
    except Exception:
        pass

    return jsonify({
        "status": "online",
        "service": "TRINETRA X Backend",
        "vision_pipeline": "disconnected",
        "database": db_status
    }), 200

@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.json
    event_id = f"EVT-{str(uuid.uuid4())[:8]}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    camera_id = data.get('camera_id', 'CAM-01')
    event_type = data.get('event_type', 'INTRUSION')
    object_type = data.get('object_type', 'person')
    confidence = data.get('confidence', 0.0)
    zone = data.get('zone', 'Restricted Zone')
    snapshot_path = data.get('snapshot_path', '')

    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO events (event_id, camera_id, timestamp, event_type, object_type, confidence, zone, snapshot_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (event_id, camera_id, timestamp, event_type, object_type, confidence, zone, snapshot_path))
        conn.commit()
        conn.close()
        
        print(f"[API INFO] Stored Event: {event_id} from {camera_id}")
        return jsonify({"message": "Event stored successfully", "event_id": event_id}), 201
    except Exception as e:
        print(f"[API ERROR] Database insertion failed: {e}")
        return jsonify({"error": "Failed to store event"}), 500

# NEW: API Endpoint to retrieve all events (ordered newest first)
@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        conn = get_db_connection()
        # Fetch all events, ordering by timestamp descending (newest at the top)
        events = conn.execute('SELECT * FROM events ORDER BY timestamp DESC').fetchall()
        conn.close()
        
        # Convert SQLite Row objects to a list of Python dictionaries
        events_list = [dict(event) for event in events]
        return jsonify(events_list), 200
    except Exception as e:
        print(f"[API ERROR] Failed to fetch events: {e}")
        return jsonify({"error": "Failed to fetch events"}), 500

# NEW: API Endpoint to get system statistics for the dashboard
@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        conn = get_db_connection()
        
        # Count total intrusions
        total_events = conn.execute('SELECT COUNT(*) FROM events').fetchone()[0]
        
        # Count total people detected in intrusions
        person_events = conn.execute("SELECT COUNT(*) FROM events WHERE object_type = 'person'").fetchone()[0]
        
        # Count total active cameras
        active_cameras = conn.execute("SELECT COUNT(*) FROM cameras WHERE status = 'ONLINE'").fetchone()[0]
        
        conn.close()
        
        return jsonify({
            "total_intrusions": total_events,
            "person_intrusions": person_events,
            "active_cameras": active_cameras
        }), 200
    except Exception as e:
        print(f"[API ERROR] Failed to fetch stats: {e}")
        return jsonify({"error": "Failed to fetch stats"}), 500

if __name__ == '__main__':
    print("[INFO] Starting TRINETRA X Backend Server...")
    app.run(host='0.0.0.0', port=5000, debug=True)