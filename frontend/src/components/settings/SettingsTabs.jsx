import React from 'react';
import './SettingsTabs.css';

function SettingsTabs({ activeTab, onTabChange }) 
{
    const tabs = [
        { id: 'general', label: 'General', enabled: true },
        { id: 'users', label: 'Users & Permissions', enabled: false },
        { id: 'praktikum', label: 'Praktikum Types & Rules', enabled: false },
        { id: 'geographical', label: 'Geographical Data', enabled: false },
    ];

    return (
        <div className="settings-tabs">
        {tabs.map((tab) => (
            <button
            key={tab.id}
            className={`settings-tab ${activeTab === tab.id ? 'active' : ''} ${!tab.enabled ? 'disabled' : ''}`}
            onClick={() => tab.enabled && onTabChange(tab.id)}
            disabled={!tab.enabled}
            title={!tab.enabled ? 'Coming in future sprint' : ''}
            >
            {tab.label}
            {!tab.enabled && <span className="coming-soon">Coming Soon</span>}
            </button>
        ))}
        </div>
    );
}

export default SettingsTabs;