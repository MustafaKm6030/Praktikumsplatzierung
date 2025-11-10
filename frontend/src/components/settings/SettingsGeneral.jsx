import React, { useState, useEffect } from 'react';
import settingsService from '../../api/settingsService';
import { getErrorMessage } from '../../api/config';
import './SettingsGeneral.css';

function SettingsGeneral() {
  const [settings, setSettings] = useState({
    id: null,
    academicYear: '',
    pdpDefaultDeadline: '',
    sfpZspDefaultDeadline: '',
    universityName: '',
    universityAddress: '',
    contactEmail: '',
    contactPhone: '',
    totalBudget: '',
    gsPercentage: '',
    msPercentage: '',
  });

  const [loading, setLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const response = await settingsService.getActive();
      const data = response.data;
      
      setSettings({
        id: data.id,
        academicYear: data.current_academic_year || '',
        pdpDefaultDeadline: data.pdp_i_demand_deadline || '',
        sfpZspDefaultDeadline: data.pl_assignment_deadline || '',
        universityName: data.university_name || '',
        universityAddress: data.university_name || '',
        contactEmail: data.contact_email || '',
        contactPhone: data.contact_phone || '',
        totalBudget: data.total_anrechnungsstunden_budget || '',
        gsPercentage: data.gs_budget_percentage || '',
        msPercentage: data.ms_budget_percentage || '',
      });
    } catch (error) {
      console.error('Error loading settings:', error);
      setSaveMessage('Fehler beim Laden der Einstellungen: ' + getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setSettings({
      ...settings,
      [field]: value,
    });
    setSaveMessage('');
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveMessage('');

    try {
      if (!settings.id) {
        setSaveMessage('Fehler: Keine aktiven Einstellungen gefunden. ❌');
        return;
      }

      const updateData = {
        current_academic_year: settings.academicYear,
        pdp_i_demand_deadline: settings.pdpDefaultDeadline,
        pl_assignment_deadline: settings.sfpZspDefaultDeadline,
        university_name: settings.universityName,
        contact_email: settings.contactEmail,
        contact_phone: settings.contactPhone,
      };

      if (settings.totalBudget) {
        updateData.total_anrechnungsstunden_budget = settings.totalBudget;
      }
      if (settings.gsPercentage) {
        updateData.gs_budget_percentage = settings.gsPercentage;
      }
      if (settings.msPercentage) {
        updateData.ms_budget_percentage = settings.msPercentage;
      }

      await settingsService.partialUpdate(settings.id, updateData);
      
      setSaveMessage('Einstellungen erfolgreich gespeichert! ✅');
      setTimeout(() => setSaveMessage(''), 3000);
      
      await loadSettings();
    } catch (error) {
      console.error('Error saving settings:', error);
      setSaveMessage('Fehler beim Speichern: ' + getErrorMessage(error) + ' ❌');
    } finally {
      setIsSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="settings-general">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Lade Einstellungen...</p>
        </div>
      </div>
    );
  }

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
            <label htmlFor="universityAddress">Address</label>
            <textarea
              id="universityAddress"
              value={settings.universityAddress}
              onChange={(e) => handleChange('universityAddress', e.target.value)}
              placeholder="Full university address"
              rows="2"
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

        {/* Budget Section */}
        <div className="settings-section">
          <h3 className="section-title">Budget Allocation</h3>
          
          <div className="form-group">
            <label htmlFor="totalBudget">Total Anrechnungsstunden Budget</label>
            <input
              type="number"
              id="totalBudget"
              value={settings.totalBudget}
              onChange={(e) => handleChange('totalBudget', e.target.value)}
              placeholder="e.g., 210"
              step="0.01"
            />
            <span className="field-hint">Total budget hours available for allocation</span>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="gsPercentage">GS Budget Percentage</label>
              <input
                type="number"
                id="gsPercentage"
                value={settings.gsPercentage}
                onChange={(e) => handleChange('gsPercentage', e.target.value)}
                placeholder="e.g., 80.48"
                step="0.01"
              />
              <span className="field-hint">Grundschule percentage</span>
            </div>

            <div className="form-group">
              <label htmlFor="msPercentage">MS Budget Percentage</label>
              <input
                type="number"
                id="msPercentage"
                value={settings.msPercentage}
                onChange={(e) => handleChange('msPercentage', e.target.value)}
                placeholder="e.g., 19.52"
                step="0.01"
              />
              <span className="field-hint">Mittelschule percentage</span>
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