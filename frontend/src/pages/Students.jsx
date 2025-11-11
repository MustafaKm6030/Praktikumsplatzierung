import React, { useState, useEffect, useCallback, useMemo } from 'react';
import studentService from '../api/studentService';
import { getErrorMessage } from '../api/config';
import { debounce } from '../utils/debounce';
import './Students.css';

function Students() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [searchTerm, setSearchTerm] = useState('');
  const [programFilter, setProgramFilter] = useState('');
  const [regionFilter, setRegionFilter] = useState('');

  const fetchStudents = useCallback(async (filters = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const params = {};
      
      if (filters.search && filters.search.trim()) {
        params.search = filters.search.trim();
      }
      
      if (filters.program) {
        params.program = filters.program;
      }
      
      if (filters.home_region) {
        params.home_region = filters.home_region;
      }
      
      const response = await studentService.getAll(params);
      setStudents(response.data);
    } catch (err) {
      const errorMsg = getErrorMessage(err);
      setError(errorMsg);
      console.error('Error fetching students:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStudents();
  }, [fetchStudents]);

  const debouncedSearch = useMemo(
    () => debounce((term) => {
      fetchStudents({ 
        search: term, 
        program: programFilter,
        home_region: regionFilter 
      });
    }, 500),
    [fetchStudents, programFilter, regionFilter]
  );

  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchTerm(value);
    debouncedSearch(value);
  };

  const handleProgramFilterChange = (e) => {
    const value = e.target.value;
    setProgramFilter(value);
    fetchStudents({ 
      search: searchTerm, 
      program: value,
      home_region: regionFilter 
    });
  };

  const handleRegionFilterChange = (e) => {
    const value = e.target.value;
    setRegionFilter(value);
    fetchStudents({ 
      search: searchTerm, 
      program: programFilter,
      home_region: value 
    });
  };

  const regionOptions = useMemo(() => {
    const uniqueRegions = [...new Set(students.map(s => s.home_region).filter(Boolean))];
    return uniqueRegions.sort();
  }, [students]);

  const handleExport = async () => {
    try {
      const response = await studentService.exportCSV();
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `students_export_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert('Fehler beim Exportieren: ' + getErrorMessage(err));
    }
  };

  const handleImport = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      await studentService.importCSV(file);
      alert('Studenten erfolgreich importiert!');
      fetchStudents();
    } catch (err) {
      alert('Fehler beim Importieren: ' + getErrorMessage(err));
    }
    e.target.value = '';
  };

  if (loading) {
    return (
      <div className="students-page">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Lade Studenten...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="students-page">
      <header className="students-header">
        <div>
          <p className="subtitle">
            Verwalten Sie Studentendaten, Fächerkombinationen und Praktikumswünsche
          </p>
        </div>
        <div className="header-actions">
          <label className="btn-secondary">
            Importieren
            <input 
              type="file" 
              accept=".csv" 
              onChange={handleImport} 
              style={{ display: 'none' }}
            />
          </label>
          <button className="btn-secondary" onClick={handleExport}>
            Exportieren
          </button>
          <button className="btn-primary" onClick={() => alert('Add Student feature coming soon')}>
            + Neuen Studenten hinzufügen
          </button>
        </div>
      </header>

      <div className="filters-section">
        <div className="search-box">
          <input
            type="text"
            placeholder="Suche nach Name, Studenten-ID oder E-Mail..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="search-input"
          />
        </div>
        
        <div className="filter-controls">
          <select 
            value={programFilter} 
            onChange={handleProgramFilterChange}
            className="filter-select"
          >
            <option value="">Alle Programme</option>
            <option value="GS">Grundschule (GS)</option>
            <option value="MS">Mittelschule (MS)</option>
          </select>

          <select 
            value={regionFilter} 
            onChange={handleRegionFilterChange}
            className="filter-select"
          >
            <option value="">Alle Regionen</option>
            {regionOptions.map(region => (
              <option key={region} value={region}>{region}</option>
            ))}
          </select>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      <div className="table-container">
        <table className="students-table">
          <thead>
            <tr>
              <th>Studenten-ID</th>
              <th>Name</th>
              <th>Programm</th>
              <th>Hauptfach</th>
              <th>Zusatzfächer</th>
              <th>E-Mail</th>
              <th>Heimatregion</th>
              <th>Zone</th>
            </tr>
          </thead>
          <tbody>
            {students.length === 0 ? (
              <tr>
                <td colSpan="8" className="empty-message">
                  {error ? 'Fehler beim Laden der Daten' : 'Keine Studenten gefunden'}
                </td>
              </tr>
            ) : (
              students.map((student) => (
                <tr key={student.id}>
                  <td className="student-id">{student.student_id}</td>
                  <td className="student-name">{student.first_name} {student.last_name}</td>
                  <td>
                    <span className={`badge badge-program-${student.program}`}>
                      {student.program === 'GS' ? 'Grundschule' : 'Mittelschule'}
                    </span>
                  </td>
                  <td>{student.primary_subject_name || 'N/A'}</td>
                  <td>
                    <div className="subjects-list">
                      {student.additional_subjects_names && student.additional_subjects_names.length > 0 
                        ? student.additional_subjects_names.join(', ')
                        : '-'}
                    </div>
                  </td>
                  <td className="email">{student.email}</td>
                  <td>
                    <span className="region-badge">{student.home_region || '-'}</span>
                  </td>
                  <td className="center">
                    <span className="zone-badge">{student.preferred_zone || '-'}</span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="table-footer">
        <div className="footer-stats">
          <span>Gesamt: <strong>{students.length}</strong> Studenten</span>
          <span>GS: <strong>{students.filter(s => s.program === 'GS').length}</strong></span>
          <span>MS: <strong>{students.filter(s => s.program === 'MS').length}</strong></span>
        </div>
      </div>
    </div>
  );
}

export default Students;
