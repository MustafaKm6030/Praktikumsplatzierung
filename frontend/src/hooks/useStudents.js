import { useState, useEffect, useCallback, useMemo } from 'react';
import studentService from '../api/studentService';
import { getErrorMessage } from '../api/config';

export default function useStudents() {
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
      if (filters.search?.trim()) params.search = filters.search.trim();
      if (filters.program) params.program = filters.program;
      if (filters.home_region) params.home_region = filters.home_region;

      const response = await studentService.getAll(params);
      setStudents(response.data);
    } catch (err) {
      setError(getErrorMessage(err));
      console.error('Error fetching students:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStudents();
  }, [fetchStudents]);

  const onSearchChange = (val) => {
    setSearchTerm(val);
    fetchStudents({
      search: val,
      program: programFilter,
      home_region: regionFilter,
    });
  };

  const onProgramChange = (val) => {
    setProgramFilter(val);
    fetchStudents({
      search: searchTerm,
      program: val,
      home_region: regionFilter,
    });
  };

  const onRegionChange = (val) => {
    setRegionFilter(val);
    fetchStudents({
      search: searchTerm,
      program: programFilter,
      home_region: val,
    });
  };

  const regionOptions = useMemo(() => {
    const unique = [...new Set(students.map((s) => s.home_region).filter(Boolean))];
    return unique.sort();
  }, [students]);

  const onExport = async () => {
    try {
      const response = await studentService.exportCSV();
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute(
        'download',
        `students_export_${new Date().toISOString().split('T')[0]}.csv`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert('Fehler beim Exportieren: ' + getErrorMessage(err));
    }
  };

  const onImport = async (e) => {
    const file = e.target.files?.[0];
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

  const stats = useMemo(() => ({
    total: students.length,
    gs: students.filter((s) => s.program === 'GS').length,
    ms: students.filter((s) => s.program === 'MS').length,
  }), [students]);

  return {
    students,
    loading,
    error,
    searchTerm,
    setSearchTerm: onSearchChange,
    programFilter,
    setProgramFilter: onProgramChange,
    regionFilter,
    setRegionFilter: onRegionChange,
    regionOptions,
    onExport,
    onImport,
    stats,
  };
}
