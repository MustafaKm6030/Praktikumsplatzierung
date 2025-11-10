import React, { useState, useEffect, useCallback, useMemo } from 'react';
import plService from '../api/plService';
import { getErrorMessage } from '../api/config';
import { debounce } from '../utils/debounce';
import './Teachers.css';

function Teachers() {
  const [pls, setPls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [searchTerm, setSearchTerm] = useState('');
  const [schulamtFilter, setSchulamtFilter] = useState('');
  const [programFilter, setProgramFilter] = useState('');

  const fetchPLs = useCallback(async (filters = {}) => {
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
      
      const response = await plService.getAll(params);
      setPls(response.data);
    } catch (err) {
      const errorMsg = getErrorMessage(err);
      setError(errorMsg);
      console.error('Error fetching PLs:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPLs();
  }, [fetchPLs]);

  const debouncedSearch = useMemo(
    () => debounce((term) => {
      fetchPLs({ search: term, program: programFilter });
    }, 500),
    [fetchPLs, programFilter]
  );

  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchTerm(value);
    debouncedSearch(value);
  };

  const handleProgramFilterChange = (e) => {
    const value = e.target.value;
    setProgramFilter(value);
    fetchPLs({ search: searchTerm, program: value });
  };

  const schulamtOptions = useMemo(() => {
    const uniqueSchulamt = [...new Set(pls.map(pl => pl.schulamt).filter(Boolean))];
    return uniqueSchulamt.sort();
  }, [pls]);

  const filteredPls = useMemo(() => {
    let filtered = [...pls];
    
    if (schulamtFilter) {
      filtered = filtered.filter(pl => pl.schulamt === schulamtFilter);
    }
    
    return filtered;
  }, [pls, schulamtFilter]);

  const totalPLs = filteredPls.length;
  const availablePLs = filteredPls.filter(pl => pl.is_available).length;

  const getPraktikumTypesDisplay = (pl) => {
    if (!pl.available_praktikum_types || pl.available_praktikum_types.length === 0) {
      return [];
    }
    
    return pl.available_praktikum_types.map(pt => {
      if (typeof pt === 'object' && pt.name) {
        return pt.name;
      } else if (typeof pt === 'object' && pt.code) {
        return pt.code;
      }
      return pt.toString();
    });
  };

  if (loading) {
    return (
      <div className="teachers-page">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Lade Praktikumslehrkräfte...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="teachers-page">
      <header className="teachers-header">
        <div>
          <h1>👨‍🏫 Praktikumslehrkräfte Verwaltung</h1>
          <p className="subtitle">
            Verwalten Sie PL Profile, Fachqualifikationen und Verfügbarkeiten
          </p>
        </div>
        <button className="btn-primary" onClick={() => alert('Add PL feature coming soon')}>
          + Neue PL hinzufügen
        </button>
      </header>

      <div className="filters-section">
        <div className="search-box">
          <input
            type="text"
            placeholder="Suche nach Name, E-Mail oder Schule..."
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
            <option value="">Alle Schularten</option>
            <option value="GS">Grundschule (GS)</option>
            <option value="MS">Mittelschule (MS)</option>
          </select>

          <select 
            value={schulamtFilter} 
            onChange={(e) => setSchulamtFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">Alle Schulämter</option>
            {schulamtOptions.map(schulamt => (
              <option key={schulamt} value={schulamt}>{schulamt}</option>
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
        <table className="pl-table">
          <thead>
            <tr>
              <th>PL ID</th>
              <th>Name</th>
              <th>Schule</th>
              <th>Schulart</th>
              <th>Hauptfach</th>
              <th>Bevorzugte Praktika</th>
              <th>Anrechnungsstd.</th>
              <th>Schulamt</th>
              <th>Max. Studierende</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {filteredPls.length === 0 ? (
              <tr>
                <td colSpan="10" className="empty-message">
                  {error ? 'Fehler beim Laden der Daten' : 'Keine Praktikumslehrkräfte gefunden'}
                </td>
              </tr>
            ) : (
              filteredPls.map((pl) => (
                <tr key={pl.id}>
                  <td className="pl-id">PL-{String(pl.id).padStart(3, '0')}</td>
                  <td className="pl-name">{pl.first_name} {pl.last_name}</td>
                  <td>{pl.school_name || 'N/A'}</td>
                  <td>
                    <span className={`badge badge-program-${pl.program}`}>
                      {pl.program_display || pl.program}
                    </span>
                  </td>
                  <td>{pl.main_subject_name || 'N/A'}</td>
                  <td>
                    <div className="praktikum-tags">
                      {getPraktikumTypesDisplay(pl).map((type, idx) => (
                        <span key={idx} className="tag">{type}</span>
                      ))}
                    </div>
                  </td>
                  <td className="center">{pl.max_simultaneous_praktikum || 2}</td>
                  <td>
                    <span className="schulamt-badge">{pl.schulamt || '-'}</span>
                  </td>
                  <td className="center">{pl.max_students_per_praktikum || 3}</td>
                  <td>
                    <span className={`status-badge ${pl.is_available ? 'status-available' : 'status-unavailable'}`}>
                      {pl.is_available ? 'Verfügbar' : 'Nicht verfügbar'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="table-footer">
        <div className="footer-stats">
          <span>Gesamt: <strong>{totalPLs}</strong> Praktikumslehrkräfte</span>
          <span>Verfügbar: <strong>{availablePLs}</strong> PLs</span>
        </div>
      </div>
    </div>
  );
}

export default Teachers;
