import React from 'react';
import './Header.css';

function Header() {
  return (
    <header className="header">
      <div className="header-left">
        <h2 className="header-title">Praktikumsamt Management System</h2>
      </div>
      
      <div className="header-right">
        <div className="header-user">
          <span className="header-user-icon">👤</span>
          <div className="header-user-info">
            <span className="header-user-name">Team 2 Admin</span>
            <span className="header-user-role">Administrator</span>
          </div>
        </div>
        
        <button className="header-logout-btn" title="Logout">
          🚪
        </button>
      </div>
    </header>
  );
}

export default Header;
