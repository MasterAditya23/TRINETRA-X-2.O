import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, Users, Video } from 'lucide-react';
import EventLog from './EventLog'; // <-- NEW IMPORT

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_intrusions: 0,
    person_intrusions: 0,
    active_cameras: 0
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/stats');
        setStats(response.data);
        setError(false);
      } catch (err) {
        console.error("Failed to connect to backend", err);
        setError(true);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  const CardStyle = {
    backgroundColor: '#1e293b',
    padding: '20px',
    borderRadius: '8px',
    border: '1px solid #334155',
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
    flex: '1',
    minWidth: '200px'
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: '600' }}>SYSTEM OVERVIEW</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: error ? '#ef4444' : '#22c55e' }}></div>
          <span style={{ fontSize: '14px', color: '#94a3b8' }}>
            {error ? 'BACKEND OFFLINE' : 'SYSTEM ONLINE'}
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginBottom: '30px' }}>
        <div style={CardStyle}>
          <div style={{ backgroundColor: '#3b82f620', padding: '12px', borderRadius: '8px' }}>
            <Activity color="#3b82f6" size={24} />
          </div>
          <div>
            <p style={{ color: '#94a3b8', fontSize: '12px', fontWeight: 'bold' }}>TOTAL INTRUSIONS</p>
            <h3 style={{ fontSize: '24px', fontWeight: 'bold' }}>{loading ? '-' : stats.total_intrusions}</h3>
          </div>
        </div>

        <div style={CardStyle}>
          <div style={{ backgroundColor: '#f59e0b20', padding: '12px', borderRadius: '8px' }}>
            <Users color="#f59e0b" size={24} />
          </div>
          <div>
            <p style={{ color: '#94a3b8', fontSize: '12px', fontWeight: 'bold' }}>PERSON DETECTIONS</p>
            <h3 style={{ fontSize: '24px', fontWeight: 'bold' }}>{loading ? '-' : stats.person_intrusions}</h3>
          </div>
        </div>

        <div style={CardStyle}>
          <div style={{ backgroundColor: '#10b98120', padding: '12px', borderRadius: '8px' }}>
            <Video color="#10b981" size={24} />
          </div>
          <div>
            <p style={{ color: '#94a3b8', fontSize: '12px', fontWeight: 'bold' }}>ACTIVE CAMERAS</p>
            <h3 style={{ fontSize: '24px', fontWeight: 'bold' }}>{loading ? '-' : stats.active_cameras}</h3>
          </div>
        </div>
      </div>

      {/* NEW: The Event Log Component is now rendered here */}
      <EventLog />
    </div>
  );
};

export default Dashboard;