import { useState, useEffect, useMemo, useCallback } from 'react';

/**
 * Teacher (PL) type – reference
 * {
 *   id,
 *   name,
 *   program ('GS' | 'MS'),
 *   schulamt,
 *   is_available,
 *   ...other fields
 * }
 */

/* -------------------- API + helper functions -------------------- */

async function fetchTeachersFromApi() {
  const res = await fetch('/api/pls');

  if (!res.ok) {
    // eslint-disable-next-line no-console
    console.error('Failed to fetch teachers:', res.status, res.statusText);
    return [];
  }

  const data = await res.json();
  return data || [];
}

function extractSchulamtOptions(teachers) {
  const options = [
    ...new Set(
      teachers
        .map(pl => pl.schulamt)
        .filter(schulamt => Boolean(schulamt))
    ),
  ];

  return options.sort();
}

function filterTeachersBySearch(teachers, searchQuery) {
  if (!searchQuery) {
    return teachers;
  }

  const q = searchQuery.toLowerCase();

  return teachers.filter(pl => {
    const name = (pl.name || '').toLowerCase();
    const id = pl.id ? String(pl.id).toLowerCase() : '';
    const email = (pl.email || '').toLowerCase();

    return (
      name.includes(q) ||
      id.includes(q) ||
      email.includes(q)
    );
  });
}

function filterTeachersByProgram(teachers, selectedProgram) {
  if (!selectedProgram || selectedProgram === 'all') {
    return teachers;
  }

  return teachers.filter(pl => pl.program === selectedProgram);
}

function filterTeachersBySchulamt(teachers, selectedSchulamt) {
  if (!selectedSchulamt || selectedSchulamt === 'all') {
    return teachers;
  }

  return teachers.filter(pl => pl.schulamt === selectedSchulamt);
}

function filterTeachers(teachers, filters) {
  const { searchQuery, selectedProgram, selectedSchulamt } = filters;
  let out = teachers;

  out = filterTeachersBySearch(out, searchQuery);
  out = filterTeachersByProgram(out, selectedProgram);
  out = filterTeachersBySchulamt(out, selectedSchulamt);

  return out;
}

function computeStats(teachers) {
  const available = teachers.filter(pl => pl.is_available).length;
  return { available };
}

/* -------------------- Small state + loader hooks -------------------- */

function useTeacherStateCore() {
  const [teachers, setTeachers] = useState([]);
  const [schulamtOptions, setSchulamtOptions] = useState([]);
  const [loading, setLoading] = useState(false);

  const programOptions = useMemo(
    function programOptionsMemo() {
      return ['GS', 'MS'];
    },
    []
  );

  return {
    teachers,
    setTeachers,
    schulamtOptions,
    setSchulamtOptions,
    loading,
    setLoading,
    programOptions,
  };
}

function useTeacherLoader(setTeachers, setSchulamtOptions, setLoading) {
  const load = useCallback(
    async function loadTeachers() {
      setLoading(true);
      try {
        const data = await fetchTeachersFromApi();
        const safe = data || [];
        setTeachers(safe);
        setSchulamtOptions(extractSchulamtOptions(safe));
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error(err);
        setTeachers([]);
        setSchulamtOptions([]);
      } finally {
        setLoading(false);
      }
    },
    [setTeachers, setSchulamtOptions, setLoading]
  );

  useEffect(() => {
    load();
  }, [load]);
}

/* -------------------- Filter state hook -------------------- */

function useTeacherFilters(teachers) {
  const [filteredTeachers, setFilteredTeachers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProgram, setSelectedProgram] = useState('all');
  const [selectedSchulamt, setSelectedSchulamt] = useState('all');

  useEffect(() => {
    const next = filterTeachers(teachers, {
      searchQuery,
      selectedProgram,
      selectedSchulamt,
    });
    setFilteredTeachers(next);
  }, [teachers, searchQuery, selectedProgram, selectedSchulamt]);

  const stats = useMemo(
    function statsMemo() {
      return computeStats(teachers);
    },
    [teachers]
  );

  return {
    filteredTeachers,
    searchQuery,
    setSearchQuery,
    selectedProgram,
    setSelectedProgram,
    selectedSchulamt,
    setSelectedSchulamt,
    stats,
  };
}

/* -------------------- Main hook (now very small) -------------------- */

export default function useTeacherData() {
  const {
    teachers,
    setTeachers,
    schulamtOptions,
    setSchulamtOptions,
    loading,
    setLoading,
    programOptions,
  } = useTeacherStateCore();

  useTeacherLoader(setTeachers, setSchulamtOptions, setLoading);

  const {
    filteredTeachers,
    searchQuery,
    setSearchQuery,
    selectedProgram,
    setSelectedProgram,
    selectedSchulamt,
    setSelectedSchulamt,
    stats,
  } = useTeacherFilters(teachers);

  return {
    teachers,
    filteredTeachers,
    loading,
    // filters
    searchQuery,
    setSearchQuery,
    selectedProgram,
    setSelectedProgram,
    selectedSchulamt,
    setSelectedSchulamt,
    // options
    programOptions,
    schulamtOptions,
    // stats
    stats,
  };
}
