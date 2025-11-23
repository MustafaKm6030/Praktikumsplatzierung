import React, { useState } from 'react';
import SettingsTabs from '../components/settings/SettingsTabs';
import SettingsGeneral from '../components/settings/SettingsGeneral';

function Settings() {
  const [activeTab, setActiveTab] = useState('general');

  return (
    <div>
      <p style={{ color: '#6b7280', marginBottom: '24px' }}>

      </p>

      <SettingsTabs activeTab={activeTab} onTabChange={setActiveTab} />

      {activeTab === 'general' && <SettingsGeneral />}

      {/* Other tabs will be added in future sprints */}
      {activeTab === 'users' && <div>Users & Permissions</div>}
      {activeTab === 'praktikum' && <div>Praktikum Types</div>}
      {activeTab === 'geographical' && <div>Geographical Data</div>}
    </div>
  );
}

export default Settings;