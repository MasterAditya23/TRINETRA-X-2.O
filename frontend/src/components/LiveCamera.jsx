import React from 'react';
import { Camera } from 'lucide-react';

const LiveCamera = ({ cameraId }) => {
  return (
    <div style={{ backgroundColor: '#1e293b', borderRadius: '8px', border: '1px solid #334155', padding: '15px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Camera color="#10b981" size={18} />
          {cameraId}
        </h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#ef4444', animation: 'pulse 2s infinite' }}></div>
          <span style={{ fontSize: '11px', color: '#ef4444', fontWeight: 'bold', letterSpacing: '1px' }}>LIVE</span>
        </div>
      </div>
      
      <div style={{ width: '100%', aspectRatio: '4/3', backgroundColor: '#000', borderRadius: '6px', overflow: 'hidden', display: 'flex', justifyContent: 'center', alignItems: 'center', border: '1px solid #475569' }}>
        <img 
          src={`http://127.0.0.1:5000/api/video_feed/${cameraId}`} 
          alt={`Live Feed ${cameraId}`} 
          style={{ width: '100%', height: '100%', objectFit: 'contain', display: 'block' }}
          onError={(e) => { e.target.style.display = 'none'; }}
        />
      </div>

      <style>
        {`
          @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.3; }
            100% { opacity: 1; }
          }
        `}
      </style>
    </div>
  );
};

export default LiveCamera;