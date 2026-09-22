import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AlertCircle, Filter, Download, Loader2, Moon } from 'lucide-react';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

const EventLog = () => {
const [events, setEvents] = useState([]);
  const [cameraFilter, setCameraFilter] = useState('ALL');
  const [objectFilter, setObjectFilter] = useState('ALL');
  const [dateFilter, setDateFilter] = useState(''); // NEW: Stores the selected date
  const [isExporting, setIsExporting] = useState(false);
  const [isNightVision, setIsNightVision] = useState(false);

  useEffect (() => {
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

  // === PASTE IT RIGHT HERE ===
  const handleNightVisionToggle = async () => {
    const newState = !isNightVision;
    setIsNightVision(newState);
    try {
      await axios.post('http://127.0.0.1:5000/api/settings/nightvision', { enabled: newState });
    } catch (error) {
      console.error("Failed to toggle night vision:", error);
      setIsNightVision(!newState); // Revert UI if API fails
    }
  };
  // ===========================

  const getFilename = (path) => {
    if (!path) return null;
    return path.split(/[\\/]/).pop();
  };

  const uniqueCameras = ['ALL', ...new Set(events.map(e => e.camera_id))];
  const uniqueObjects = ['ALL', ...new Set(events.map(e => e.object_type))];

const filteredEvents = events.filter(event => {
    const matchCamera = cameraFilter === 'ALL' || event.camera_id === cameraFilter;
    const matchObject = objectFilter === 'ALL' || event.object_type === objectFilter;
    
    // Extract just the "YYYY-MM-DD" part from the database timestamp
    const eventDate = event.timestamp ? event.timestamp.split(' ')[0] : '';
    // Match the date only if a date is actually selected in the calendar
    const matchDate = dateFilter === '' || eventDate === dateFilter;
    
    return matchCamera && matchObject && matchDate;
  });

  // Helper function to convert image URLs to Base64 for the PDF
  const getBase64ImageFromUrl = async (url) => {
    try {
      const response = await fetch(url);
      
      // Stop if Flask returns a 404 Error (Missing image)
      if (!response.ok) return null; 
      
      const blob = await response.blob();
      
      // Ensure it is actually an image before parsing to prevent jsPDF crash
      if (!blob.type.startsWith('image/')) return null; 

      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
    } catch (e) {
      console.error("Failed to load image for PDF:", e);
      return null;
    }
  };

  const exportToPDF = async () => {
    setIsExporting(true); // Show loading state
    
    try {
      const doc = new jsPDF();
      
      // Header
      doc.setFontSize(18);
      doc.setTextColor(220, 38, 38); 
      doc.text("TRINETRA X - Critical Incident Report", 14, 22);
      
      doc.setFontSize(11);
      doc.setTextColor(100);
      doc.text(`Generated on: ${new Date().toLocaleString()}`, 14, 30);
      doc.text(`Active Filters - Camera: ${cameraFilter} | Object: ${objectFilter}`, 14, 36);

      const tableColumn = ["EVIDENCE", "TIME", "EVENT ID", "CAMERA", "OBJECT"];
      const tableRows = [];
      const base64Images = []; 

      // 1. Prepare data and fetch all images
      for (const event of filteredEvents) {
        let imgData = null;
        if (event.snapshot_path) {
          const filename = getFilename(event.snapshot_path);
          imgData = await getBase64ImageFromUrl(`http://127.0.0.1:5000/api/snapshots/${filename}`);
        }
        base64Images.push(imgData);
        
        tableRows.push([
          "", // Leave blank for the image
          event.timestamp,
          event.event_id,
          event.camera_id,
          event.object_type.toUpperCase()
        ]);
      }

// 2. Generate the table with AutoTable (UPDATED SYNTAX)
      autoTable(doc, {
        head: [tableColumn],
        body: tableRows,
        startY: 42,
        theme: 'grid',
        styles: { fontSize: 10, valign: 'middle' },
        headStyles: { fillColor: [30, 41, 59] },
        columnStyles: { 
          0: { cellWidth: 40, minCellHeight: 25 } 
        },
        didDrawCell: function (data) {
          if (data.column.index === 0 && data.cell.section === 'body') {
            const imgData = base64Images[data.row.index];
            if (imgData) {
              doc.addImage(imgData, 'JPEG', data.cell.x + 2, data.cell.y + 2, 36, 21);
            }
          }
        }
      });

      doc.save(`TRINETRA_Report_${new Date().getTime()}.pdf`);
    } catch (error) {
      console.error("Critical error generating PDF:", error);
      alert("An error occurred while generating the PDF. Check the console for details.");
    } finally {
      setIsExporting(false); // This guarantees the button always resets
    }
  };

  return (
    <div style={{ backgroundColor: '#1e293b', borderRadius: '8px', border: '1px solid #334155', padding: '20px' }}>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '15px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <AlertCircle color="#ef4444" size={20} />
          LIVE INCIDENT FEED
        </h2>

        <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
          <Filter size={16} color="#94a3b8" />
          
          <select 
            value={cameraFilter} 
            onChange={(e) => setCameraFilter(e.target.value)}
            style={{ backgroundColor: '#0f172a', color: '#f8fafc', border: '1px solid #475569', padding: '8px 12px', borderRadius: '4px', fontSize: '14px', outline: 'none', cursor: 'pointer' }}
          >
            {uniqueCameras.map(cam => (
              <option key={cam} value={cam}>{cam === 'ALL' ? 'All Cameras' : cam}</option>
            ))}
          </select>

          <select 
            value={objectFilter} 
            onChange={(e) => setObjectFilter(e.target.value)}
            style={{ backgroundColor: '#0f172a', color: '#f8fafc', border: '1px solid #475569', padding: '8px 12px', borderRadius: '4px', fontSize: '14px', outline: 'none', cursor: 'pointer' }}
          >
            {uniqueObjects.map(obj => (
              <option key={obj} value={obj}>{obj === 'ALL' ? 'All Objects' : obj.toUpperCase()}</option>
            ))}
          </select>

          {/* NEW: Date Picker UI */}
          <input 
            type="date"
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
            style={{ backgroundColor: '#0f172a', color: '#f8fafc', border: '1px solid #475569', padding: '8px 12px', borderRadius: '4px', fontSize: '14px', outline: 'none', cursor: 'pointer', colorScheme: 'dark' }}
          />

          {/* NEW: Clear Date Button (Only shows if a date is selected) */}
          {dateFilter && (
            <button 
              onClick={() => setDateFilter('')}
              style={{ backgroundColor: 'transparent', color: '#ef4444', border: '1px solid #ef4444', padding: '8px 12px', borderRadius: '4px', fontSize: '14px', cursor: 'pointer' }}
            >
              Clear Date
            </button>
          )}
           {/* NEW: Night Vision Toggle */}
          <button 
            onClick={handleNightVisionToggle}
            style={{ display: 'flex', alignItems: 'center', gap: '8px', backgroundColor: isNightVision ? '#22c55e' : '#334155', color: isNightVision ? '#0f172a' : '#f8fafc', border: '1px solid #475569', padding: '8px 16px', borderRadius: '4px', fontSize: '14px', fontWeight: 'bold', cursor: 'pointer', transition: 'all 0.2s' }}
          >
            <Moon size={16} fill={isNightVision ? "#0f172a" : "none"} />
            {isNightVision ? 'NIGHT MODE: ON' : 'NIGHT MODE'}
          </button>
          <button 
            onClick={exportToPDF}
            disabled={isExporting}
            style={{ display: 'flex', alignItems: 'center', gap: '8px', backgroundColor: isExporting ? '#64748b' : '#3b82f6', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '4px', fontSize: '14px', fontWeight: 'bold', cursor: isExporting ? 'not-allowed' : 'pointer', transition: 'background-color 0.2s' }}
          >
            {isExporting ? <Loader2 size={16} className="animate-spin" /> : <Download size={16} />}
            {isExporting ? 'GENERATING...' : 'EXPORT PDF'}
          </button>
        </div>
      </div>

      <style>
        {`
          .animate-spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>

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
            {filteredEvents.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>
                  No matching events found.
                </td>
              </tr>
            ) : (
              filteredEvents.map((event, index) => (
                <tr key={index} style={{ borderBottom: '1px solid #334155', backgroundColor: index % 2 === 0 ? 'transparent' : '#0f172a' }}>
                  <td style={{ padding: '12px' }}>
                    {event.snapshot_path ? (
                      <img 
                        src={`http://127.0.0.1:5000/api/snapshots/${getFilename(event.snapshot_path)}`} 
                        alt="Evidence Snapshot" 
                        style={{ height: '40px', width: '70px', objectFit: 'cover', borderRadius: '4px', border: '1px solid #475569' }}
                        onError={(e) => { e.target.style.display = 'none'; }}
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