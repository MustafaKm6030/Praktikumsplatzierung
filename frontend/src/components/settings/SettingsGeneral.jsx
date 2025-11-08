import React, { useState } from 'react';
import './SettingsGeneral.css';

function SettingsGeneral() {
  // Dummy data - will be replaced with API call
  const [settings, setSettings] = useState({
    academicYear: '2024/2025',
    pdpDefaultDeadline: '2025-05-01',
    sfpZspDefaultDeadline: '2025-06-15',
    universityName: 'Universität Passau',
    universityAddress: 'Innstraße 41, 94032 Passau',
    contactEmail: 'praktikumsamt@uni-passau.de',
    contactPhone: '+49 851 509-0',
  });

  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  const handleChange = (field, value) => {
    setSettings({
      ...settings,
      [field]: value,
    });
    setSaveMessage(''); // Clear save message when editing
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveMessage('');

    try {
      // TODO: Replace with actual API call when backend is ready
      // await axios.put('/api/settings', settings);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSaveMessage('Settings saved successfully! ✅');
      setTimeout(() => setSaveMessage(''), 3000);
    } catch (error) {
      setSaveMessage('Error saving settings. Please try again. ❌');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="settings-general">
      <h2 className="settings-general-title">General Settings</h2>
      <p className="settings-general-subtitle">
        Configure core system settings including academic year, deadlines, and university information.
      </p>

      <form onSubmit={handleSave} className="settings-form">
        {/* Academic Year Section */}
        <div className="settings-section">
          <h3 className="section-title">Academic Year</h3>
          
          <div className="form-group">
            <label htmlFor="academicYear">Current Academic Year *</label>
            <input
              type="text"
              id="academicYear"
              value={settings.academicYear}
              onChange={(e) => handleChange('academicYear', e.target.value)}
              placeholder="e.g., 2024/2025"
              required
            />
            <span className="field-hint">Format: YYYY/YYYY</span>
          </div>
        </div>

        {/* Deadlines Section */}
        <div className="settings-section">
          <h3 className="section-title">Praktikum Deadlines</h3>
          
          <div className="form-group">
            <label htmlFor="pdpDefaultDeadline">PDP I/II Default Deadline *</label>
            <input
              type="date"
              id="pdpDefaultDeadline"
              value={settings.pdpDefaultDeadline}
              onChange={(e) => handleChange('pdpDefaultDeadline', e.target.value)}
              required
            />
            <span className="field-hint">Default deadline for block internships (PDP I & PDP II)</span>
          </div>

          <div className="form-group">
            <label htmlFor="sfpZspDefaultDeadline">SFP/ZSP Default Deadline *</label>
            <input
              type="date"
              id="sfpZspDefaultDeadline"
              value={settings.sfpZspDefaultDeadline}
              onChange={(e) => handleChange('sfpZspDefaultDeadline', e.target.value)}
              required
            />
            <span className="field-hint">Default deadline for Wednesday internships (SFP & ZSP)</span>
          </div>
        </div>

        {/* University Information Section */}
        <div className="settings-section">
          <h3 className="section-title">University Information</h3>
          
          <div className="form-group">
            <label htmlFor="universityName">University Name *</label>
            <input
              type="text"
              id="universityName"
              value={settings.universityName}
              onChange={(e) => handleChange('universityName', e.target.value)}
              placeholder="e.g., Universität Passau"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="universityAddress">Address *</label>
            <textarea
              id="universityAddress"
              value={settings.universityAddress}
              onChange={(e) => handleChange('universityAddress', e.target.value)}
              placeholder="Full university address"
              rows="2"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="contactEmail">Contact Email *</label>
              <input
                type="email"
                id="contactEmail"
                value={settings.contactEmail}
                onChange={(e) => handleChange('contactEmail', e.target.value)}
                placeholder="email@uni-passau.de"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="contactPhone">Contact Phone</label>
              <input
                type="tel"
                id="contactPhone"
                value={settings.contactPhone}
                onChange={(e) => handleChange('contactPhone', e.target.value)}
                placeholder="+49 851 509-0"
              />
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="settings-actions">
          <button 
            type="submit" 
            className="btn-save"
            disabled={isSaving}
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
          
          {saveMessage && (
            <span className={`save-message ${saveMessage.includes('✅') ? 'success' : 'error'}`}>
              {saveMessage}
            </span>
          )}
        </div>
      </form>
    </div>
  );
}

export default SettingsGeneral;