import React from 'react';
import { ShieldAlert } from 'lucide-react';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <div style={{ padding: '30px', maxWidth: '1200px', margin: '0 auto' }}>
      <header style={{ display: 'flex', alignItems: 'center', gap: '15px', borderBottom: '1px solid #1e293b', paddingBottom: '20px', marginBottom: '30px' }}>
        <ShieldAlert size={36} color="#3b82f6" />
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 'bold', letterSpacing: '1px', margin: 0 }}>TRINETRA X</h1>
          <p style={{ color: '#94a3b8', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '2px', margin: 0, marginTop: '4px' }}>AI Border Surveillance Command Centre</p>
        </div>
      </header>
      
      <main>
        <Dashboard />
      </main>
    </div>
  );
}

export default App;