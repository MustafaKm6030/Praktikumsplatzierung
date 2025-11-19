// frontend/src/components/teachers/useTeacherData.js
import { useState, useEffect, useCallback, useMemo } from 'react';

/**
 * ---- Types (for reference) ----
 * Teacher = {
 *   id, first_name, last_name, email, school_name,
 *   program, program_display, main_subject_name,
 *   available_praktikum_types: Array<string|{name?:string, code?:string}>,
 *   max_simultaneous_praktikum, max_students_per_praktikum,
 *   schulamt, is_available
 * }
 */

/* -------------------- Small pure helpers -------------------- */

/** Fetch list of PLs (teachers) from API. Swap to plService if you prefer. */
async function fetchTeachersFromApi() {
  const res = await fetch('/api/pls');
  if (!res.ok) {
    throw new Error(`Failed to fetch PLs: ${res.status} ${res.statusText}`);}
  return res.json();
}

/** Derive unique Schulamt options from data */
function extractSchulamtOptions(list) {
  return [...new Set((list || []).map(pl => pl?.schulamt).filter(Boolean))];
}

/** Case-insensitive includes */
function includesCI(haystack, needle) {
  if (!haystack || !needle) return false;
  return String(haystack).toLowerCase().includes(String(needle).toLowerCase());
}

/** Apply all filters to the list */
function filterTeachers(list, { searchQuery, selectedProgram, selectedSchulamt }) {
  let out = list || [];

  if (searchQuery) {
    out = out.filter(pl =>
      includesCI(pl.first_name, searchQuery) ||
      includesCI(pl.last_name, searchQuery) ||
      includesCI(pl.email, searchQuery) ||
      includesCI(pl.school_name, searchQuery)
    );
  }

  if (selectedProgram && selectedProgram !== 'all') {
    out = out.filter(pl => pl.program === selectedProgram);
  }

  if (selectedSchulamt && selectedSchulamt !== 'all') {
    out = out.filter(pl => pl.schulamt === selectedSchulamt);
  }

  return out;
}

/* -------------------- Main hook (now short) -------------------- */

export default function useTeacherData() {
  const [teachers, setTeachers] = useState([]);
  const [filteredTeachers, setFilteredTeachers] = useState([]);
  const [loading, setLoading] = useState(false);

  // filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProgram, setSelectedProgram] = useState('all');
  const [selectedSchulamt, setSelectedSchulamt] = useState('all');

  // options (programs fixed; schulamt derived)
  const programOptions = useMemo(() => ['GS', 'MS'], []);
  const [schulamtOptions, setSchulamtOptions] = useState([]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchTeachersFromApi();
      setTeachers(data || []);
      setSchulamtOptions(extractSchulamtOptions(data || []));
      // initial filtered view = full list
      setFilteredTeachers(data || []);
    } catch (err) {
      console.error(err);
      setTeachers([]);
      setFilteredTeachers([]);
      setSchulamtOptions([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // initial/data reload
  useEffect(() => {
    void load();
  }, [load]);

  // re-apply filters whenever inputs change
  useEffect(() => {
    setFilteredTeachers(
      filterTeachers(teachers, { searchQuery, selectedProgram, selectedSchulamt })
    );
  }, [teachers, searchQuery, selectedProgram, selectedSchulamt]);

  // quick stats for header
  const stats = useMemo(
    () => ({ available: teachers.filter(pl => pl.is_available).length }),
    [teachers]
  );

  return {
    teachers,
    filteredTeachers,
    loading,
    // filters
    searchQuery, setSearchQuery,
    selectedProgram, setSelectedProgram,
    selectedSchulamt, setSelectedSchulamt,
    // options
    programOptions,
    schulamtOptions,
    // stats
    stats,
  };
}
