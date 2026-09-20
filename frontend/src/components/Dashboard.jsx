import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Activity, Users, Video, AlertTriangle } from 'lucide-react';
import EventLog from './EventLog';
import LiveCamera from './LiveCamera';

const Dashboard = () => {
  const [stats, setStats] = useState({ total_intrusions: 0, person_intrusions: 0, active_cameras: 0 });
  const [cameras, setCameras] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  
  // NEW: Alarm State
  const [isAlarmActive, setIsAlarmActive] = useState(false);
  const prevIntrusions = useRef(null);

  // NEW: Synthesized Siren Sound (No MP3 required!)
  const playSiren = () => {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.type = 'square';
    
    // Create a high-low-high-low siren pitch
    osc.frequency.setValueAtTime(880, ctx.currentTime);      // High pitch
    osc.frequency.setValueAtTime(440, ctx.currentTime + 0.5); // Low pitch
    osc.frequency.setValueAtTime(880, ctx.currentTime + 1.0); // High pitch
    osc.frequency.setValueAtTime(440, ctx.currentTime + 1.5); // Low pitch
    
    gain.gain.setValueAtTime(0.1, ctx.currentTime); // Volume (0.1 is safe/moderate)
    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + 2.0);
  };

  const triggerAlarm = () => {
    setIsAlarmActive(true);
    playSiren();
    // Turn off the visual flashing after 3 seconds
    setTimeout(() => setIsAlarmActive(false), 3000);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, camsRes] = await Promise.all([
          axios.get('http://127.0.0.1:5000/api/stats'),
          axios.get('http://127.0.0.1:5000/api/cameras')
        ]);
        
        const newStats = statsRes.data;
        setStats(newStats);
        setCameras(camsRes.data);
        setError(false);

        // ALARM LOGIC: If total intrusions increased, sound the alarm!
        if (prevIntrusions.current !== null && newStats.total_intrusions > prevIntrusions.current) {
          triggerAlarm();
        }
        prevIntrusions.current = newStats.total_intrusions;

      } catch (err) {
        console.error("Failed to connect to backend", err);
        setError(true);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    // Speed up polling to 2 seconds so the alarm triggers faster for the live demo!
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const CardStyle = { backgroundColor: '#1e293b', padding: '20px', borderRadius: '8px', border: '1px solid #334155', display: 'flex', alignItems: 'center', gap: '15px', flex: '1', minWidth: '200px' };

  return (
    <div>
      {/* NEW: CRITICAL ALERT FULL-SCREEN OVERLAY */}
      {isAlarmActive && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          border: '10px solid #ef4444', backgroundColor: 'rgba(239, 68, 68, 0.15)',
          pointerEvents: 'none', zIndex: 9999, animation: 'flash 0.5s infinite'
        }}>
          <div style={{ 
            position: 'absolute', top: '20px', left: '50%', transform: 'translateX(-50%)', 
            backgroundColor: '#ef4444', color: 'white', padding: '15px 30px', 
            borderRadius: '8px', fontWeight: 'bold', display: 'flex', alignItems: 'center', 
            gap: '15px', fontSize: '24px', boxShadow: '0 4px 6px rgba(0,0,0,0.3)'
          }}>
            <AlertTriangle size={32} /> CRITICAL INTRUSION DETECTED <AlertTriangle size={32} />
          </div>
        </div>
      )}

      {/* Required for the flashing animation */}
      <style>
        {`
          @keyframes flash {
            0% { opacity: 1; }
            50% { opacity: 0.2; }
            100% { opacity: 1; }
          }
        `}
      </style>

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

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        {cameras.map((cam) => (
          <LiveCamera key={cam.id} cameraId={cam.id} />
        ))}
      </div>

      <EventLog />
    </div>
  );
};

export default Dashboard;