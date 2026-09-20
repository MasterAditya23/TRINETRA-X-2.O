import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AlertCircle } from 'lucide-react';

const EventLog = () => {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/events');
        setEvents(response.data);
      } catch (error) {
        console.error("Error fetching events:", error);
      }
    };

    fetchEvents();
    const interval = setInterval(fetchEvents, 3000);
    return () => clearInterval(interval);
  }, []);

  // Helper function to extract just the filename from a file path
  const getFilename = (path) => {
    if (!path) return null;
    return path.split(/[\\/]/).pop();
  };

  return (
    <div style={{ backgroundColor: '#1e293b', borderRadius: '8px', border: '1px solid #334155', padding: '20px' }}>
      <h2 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <AlertCircle color="#ef4444" size={20} />
        LIVE INCIDENT FEED
      </h2>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8', fontSize: '12px' }}>
              <th style={{ padding: '12px' }}>EVIDENCE</th>
              <th style={{ padding: '12px' }}>TIME</th>
              <th style={{ padding: '12px' }}>EVENT ID</th>
              <th style={{ padding: '12px' }}>CAMERA</th>
              <th style={{ padding: '12px' }}>OBJECT</th>
            </tr>
          </thead>
          <tbody>
            {events.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>No events recorded yet.</td>
              </tr>
            ) : (
              events.map((event, index) => (
                <tr key={index} style={{ borderBottom: '1px solid #334155', backgroundColor: index % 2 === 0 ? 'transparent' : '#0f172a' }}>
                  
                  {/* NEW: Evidence Thumbnail Column */}
                  <td style={{ padding: '12px' }}>
                    {event.snapshot_path ? (
                      <img 
                        src={`http://127.0.0.1:5000/api/snapshots/${getFilename(event.snapshot_path)}`} 
                        alt="Evidence Snapshot" 
                        style={{ height: '40px', width: '70px', objectFit: 'cover', borderRadius: '4px', border: '1px solid #475569' }}
                        onError={(e) => { e.target.style.display = 'none'; }} // Hide if image broken
                      />
                    ) : (
                      <span style={{ color: '#64748b', fontSize: '12px' }}>No Image</span>
                    )}
                  </td>

                  <td style={{ padding: '12px', fontSize: '14px', color: '#cbd5e1' }}>{event.timestamp}</td>
                  <td style={{ padding: '12px', fontSize: '14px', fontFamily: 'monospace', color: '#3b82f6' }}>{event.event_id}</td>
                  <td style={{ padding: '12px', fontSize: '14px' }}>{event.camera_id}</td>
                  <td style={{ padding: '12px', fontSize: '14px', textTransform: 'uppercase', color: '#f59e0b', fontWeight: 'bold' }}>{event.object_type}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default EventLog;