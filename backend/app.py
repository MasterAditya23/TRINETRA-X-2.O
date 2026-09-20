import os
import sys
from flask import Flask, jsonify, request, send_from_directory, Response
from flask_cors import CORS
import uuid
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)

from database.db import get_db_connection
from vision.streamer import generate_frames

app = Flask(__name__)
CORS(app)

# ==========================================
# CAMERA CONFIGURATION (FOR SIH LIVE DEMO)
# ==========================================
# Change '0' to your phone's IP Webcam URL when ready!
# Example: 'CAM-02': 'http://192.168.1.5:8080/video'
CAMERAS = {
    'CAM-01': 0, 
    'CAM-02': 'http://10.179.146.133:8080/video', 
    'CAM-03': None, 
    'CAM-04': None  
}

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "online"}), 200

@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.json
    event_id = f"EVT-{str(uuid.uuid4())[:8]}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO events (event_id, camera_id, timestamp, event_type, object_type, confidence, zone, snapshot_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (event_id, data.get('camera_id'), timestamp, data.get('event_type'), data.get('object_type'), data.get('confidence'), data.get('zone'), data.get('snapshot_path')))
        conn.commit()
        conn.close()
        return jsonify({"message": "Event stored", "event_id": event_id}), 201
    except Exception as e:
        return jsonify({"error": "Failed to store event"}), 500

@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        conn = get_db_connection()
        events = conn.execute('SELECT * FROM events ORDER BY timestamp DESC').fetchall()
        conn.close()
        return jsonify([dict(event) for event in events]), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch events"}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        conn = get_db_connection()
        total = conn.execute('SELECT COUNT(*) FROM events').fetchone()[0]
        persons = conn.execute("SELECT COUNT(*) FROM events WHERE object_type = 'person'").fetchone()[0]
        # Active cameras calculation based on our dictionary
        active_cameras = sum(1 for cam in CAMERAS.values() if cam is not None)
        conn.close()
        return jsonify({"total_intrusions": total, "person_intrusions": persons, "active_cameras": active_cameras}), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch stats"}), 500

@app.route('/api/snapshots/<filename>', methods=['GET'])
def get_snapshot(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'data', 'snapshots'), filename)

# NEW: Dynamic Multi-Camera Video Routing
@app.route('/api/video_feed/<camera_id>')
def video_feed(camera_id):
    if camera_id not in CAMERAS or CAMERAS[camera_id] is None:
        return "Camera offline or not configured", 404
        
    camera_source = CAMERAS[camera_id]
    return Response(generate_frames(camera_source, camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')

# Endpoint for frontend to know which cameras are configured
@app.route('/api/cameras', methods=['GET'])
def get_cameras():
    active_cams = [{"id": cam_id, "status": "ONLINE"} for cam_id, source in CAMERAS.items() if source is not None]
    return jsonify(active_cams), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)