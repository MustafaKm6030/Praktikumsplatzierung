import { useState, useEffect, useCallback, useMemo } from 'react';
// If you already have plService/getErrorMessage you can swap fetch() with it.

const useTeacherData = () => {
  const [teachers, setTeachers] = useState([]);
  const [filteredTeachers, setFilteredTeachers] = useState([]);
  const [loading, setLoading] = useState(false);

  // filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProgram, setSelectedProgram] = useState('all');
  const [selectedSchulamt, setSelectedSchulamt] = useState('all');

  // options
  const [programOptions] = useState(['GS', 'MS']); // fixed
  const [schulamtOptions, setSchulamtOptions] = useState([]);

  const extractOptions = useCallback((data) => {
    const uniqueSchulamt = [...new Set((data || []).map(pl => pl.schulamt).filter(Boolean))];
    setSchulamtOptions(uniqueSchulamt);
  }, []);

  const fetchTeachers = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/pls'); // mirror your old endpoint
      if (!res.ok) {
        console.error('Failed to fetch PLs:', res.status, res.statusText);
        setTeachers([]);
        setFilteredTeachers([]);
        return;
      }
      const data = await res.json();
      setTeachers(data || []);
      setFilteredTeachers(data || []);
      extractOptions(data || []);
    } catch (err) {
      console.error('Error fetching PLs:', err);
    } finally {
      setLoading(false);
    }
  }, [extractOptions]);

  useEffect(() => {
    void fetchTeachers();
  }, [fetchTeachers]);

  // filtering
  useEffect(() => {
    let filtered = teachers;

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter(pl =>
        (pl.first_name && pl.first_name.toLowerCase().includes(q)) ||
        (pl.last_name && pl.last_name.toLowerCase().includes(q)) ||
        (pl.email && pl.email.toLowerCase().includes(q)) ||
        (pl.school_name && pl.school_name.toLowerCase().includes(q))
      );
    }

    if (selectedProgram !== 'all') {
      filtered = filtered.filter(pl => pl.program === selectedProgram);
    }

    if (selectedSchulamt !== 'all') {
      filtered = filtered.filter(pl => pl.schulamt === selectedSchulamt);
    }

    setFilteredTeachers(filtered);
  }, [searchQuery, selectedProgram, selectedSchulamt, teachers]);

  const stats = useMemo(() => {
    const available = teachers.filter(pl => pl.is_available).length;
    return { available };
  }, [teachers]);

  return {
    teachers,
    filteredTeachers,
    loading,
    searchQuery, setSearchQuery,
    selectedProgram, setSelectedProgram,
    selectedSchulamt, setSelectedSchulamt,
    programOptions,
    schulamtOptions,
    stats,
  };
};

export default useTeacherData;
