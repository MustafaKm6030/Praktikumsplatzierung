import React, { useState } from 'react';
import SettingsTabs from '../components/settings/SettingsTabs';
import SettingsGeneral from '../components/settings/SettingsGeneral';

function Settings() {
  const [activeTab, setActiveTab] = useState('general');

  return (
    <div>
      <p style={{ color: '#6b7280', marginBottom: '24px' }}>
        Configure system-wide parameters, deadlines, and information.
      </p>

      <SettingsTabs activeTab={activeTab} onTabChange={setActiveTab} />

      {activeTab === 'general' && <SettingsGeneral />}
      
      {/* Other tabs will be added in future sprints */}
      {activeTab === 'users' && <div>Users & Permissions - Coming Soon</div>}
      {activeTab === 'praktikum' && <div>Praktikum Types - Coming Soon</div>}
      {activeTab === 'geographical' && <div>Geographical Data - Coming Soon</div>}
    </div>
  );
}

export default Settings;