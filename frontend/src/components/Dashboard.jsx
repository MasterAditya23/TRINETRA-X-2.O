import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, Users, Video } from 'lucide-react';
import EventLog from './EventLog';
import LiveCamera from './LiveCamera';

const Dashboard = () => {
  const [stats, setStats] = useState({ total_intrusions: 0, person_intrusions: 0, active_cameras: 0 });
  const [cameras, setCameras] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, camsRes] = await Promise.all([
          axios.get('http://127.0.0.1:5000/api/stats'),
          axios.get('http://127.0.0.1:5000/api/cameras')
        ]);
        setStats(statsRes.data);
        setCameras(camsRes.data);
        setError(false);
      } catch (err) {
        console.error("Failed to connect to backend", err);
        setError(true);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const CardStyle = { backgroundColor: '#1e293b', padding: '20px', borderRadius: '8px', border: '1px solid #334155', display: 'flex', alignItems: 'center', gap: '15px', flex: '1', minWidth: '200px' };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: '600' }}>SYSTEM OVERVIEW</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: error ? '#ef4444' : '#22c55e' }}></div>
          <span style={{ fontSize: '14px', color: '#94a3b8' }}>{error ? 'BACKEND OFFLINE' : 'SYSTEM ONLINE'}</span>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginBottom: '30px' }}>
        <div style={CardStyle}>
          <div style={{ backgroundColor: '#3b82f620', padding: '12px', borderRadius: '8px' }}><Activity color="#3b82f6" size={24} /></div>
          <div><p style={{ color: '#94a3b8', fontSize: '12px', fontWeight: 'bold' }}>TOTAL INTRUSIONS</p><h3 style={{ fontSize: '24px', fontWeight: 'bold' }}>{loading ? '-' : stats.total_intrusions}</h3></div>
        </div>
        <div style={CardStyle}>
          <div style={{ backgroundColor: '#f59e0b20', padding: '12px', borderRadius: '8px' }}><Users color="#f59e0b" size={24} /></div>
          <div><p style={{ color: '#94a3b8', fontSize: '12px', fontWeight: 'bold' }}>PERSON DETECTIONS</p><h3 style={{ fontSize: '24px', fontWeight: 'bold' }}>{loading ? '-' : stats.person_intrusions}</h3></div>
        </div>
        <div style={CardStyle}>
          <div style={{ backgroundColor: '#10b98120', padding: '12px', borderRadius: '8px' }}><Video color="#10b981" size={24} /></div>
          <div><p style={{ color: '#94a3b8', fontSize: '12px', fontWeight: 'bold' }}>ACTIVE CAMERAS</p><h3 style={{ fontSize: '24px', fontWeight: 'bold' }}>{loading ? '-' : stats.active_cameras}</h3></div>
        </div>
      </div>

      {/* DYNAMIC CAMERA GRID */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', 
        gap: '20px', 
        marginBottom: '30px' 
      }}>
        {cameras.map((cam) => (
          <LiveCamera key={cam.id} cameraId={cam.id} />
        ))}
      </div>

      <EventLog />
    </div>
  );
};

export default Dashboard;