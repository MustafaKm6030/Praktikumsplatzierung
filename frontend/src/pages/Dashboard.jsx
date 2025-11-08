import React from 'react';

function Dashboard() {
  return (
    <div>
      <h1>📊 Dashboard</h1>
      <p>Welcome to the Praktikumsamt Management System!</p>
      <div style={{ marginTop: '20px', padding: '20px', backgroundColor: '#f0f9ff', borderRadius: '8px', border: '1px solid #bfdbfe' }}>
        <h3>Sprint 1 Progress</h3>
        <p>✅ Navigation structure implemented</p>
        <p>🔄 Student management in progress...</p>
        <p>⏳ Teacher management coming soon</p>
      </div>
    </div>
  );
}

export default Dashboard;
