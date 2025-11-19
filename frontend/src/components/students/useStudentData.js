import { useState, useEffect, useCallback, useMemo } from 'react';

/**
 * Student type (reference)
 * {
 *   id, student_id, first_name, last_name,
 *   program ('GS'|'MS'), primary_subject_name, additional_subjects_names[],
 *   email, home_region, preferred_zone
 * }
 */

function useStudentBase() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);

  // options
  const [programs, setPrograms] = useState(['GS', 'MS']);
  const [regions, setRegions] = useState([]);

  const extractOptions = useCallback(
    function extractOptions(data) {
      const uniqueRegions = [
        ...new Set(
          data
            .map((s) => s.home_region)
            .filter((region) => Boolean(region))
        ),
      ];
      setRegions(uniqueRegions);
      setPrograms(['GS', 'MS']); // fixed, but you can derive if needed
    },
    []
  );

  const fetchStudents = useCallback(
    async function fetchStudentsCallback() {
      setLoading(true);
      try {
        const res = await fetch('/api/students');
        if (!res.ok) {
          // eslint-disable-next-line no-console
          console.error('Failed to fetch students:', res.status, res.statusText);
          setStudents([]);
          return;
        }
        const data = await res.json();
        const safeData = data || [];
        setStudents(safeData);
        extractOptions(safeData);
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error('Error fetching students:', err);
      } finally {
        setLoading(false);
      }
    },
    [extractOptions]
  );

  useEffect(() => {
    fetchStudents();
  }, [fetchStudents]);

  return {
    students,
    loading,
    programs,
    regions,
  };
}

function useStudentFilters(students) {
  const [filteredStudents, setFilteredStudents] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProgram, setSelectedProgram] = useState('all');
  const [selectedRegion, setSelectedRegion] = useState('all');

  useEffect(() => {
    let filtered = students;

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (s) =>
          (s.first_name && s.first_name.toLowerCase().includes(q)) ||
          (s.last_name && s.last_name.toLowerCase().includes(q)) ||
          (s.student_id && String(s.student_id).toLowerCase().includes(q)) ||
          (s.email && s.email.toLowerCase().includes(q))
      );
    }

    if (selectedProgram !== 'all') {
      filtered = filtered.filter((s) => s.program === selectedProgram);
    }

    if (selectedRegion !== 'all') {
      filtered = filtered.filter((s) => s.home_region === selectedRegion);
    }

    setFilteredStudents(filtered);
  }, [searchQuery, selectedProgram, selectedRegion, students]);

  const stats = useMemo(
    function computeStats() {
      const gs = students.filter((s) => s.program === 'GS').length;
      const ms = students.filter((s) => s.program === 'MS').length;
      return { gs, ms };
    },
    [students]
  );

  return {
    filteredStudents,
    searchQuery,
    setSearchQuery,
    selectedProgram,
    setSelectedProgram,
    selectedRegion,
    setSelectedRegion,
    stats,
  };
}

const useStudentData = () => {
  const { students, loading, programs, regions } = useStudentBase();

  const {
    filteredStudents,
    searchQuery,
    setSearchQuery,
    selectedProgram,
    setSelectedProgram,
    selectedRegion,
    setSelectedRegion,
    stats,
  } = useStudentFilters(students);

  return {
    students,
    filteredStudents,
    loading,
    searchQuery,
    setSearchQuery,
    selectedProgram,
    setSelectedProgram,
    selectedRegion,
    setSelectedRegion,
    programs,
    regions,
    stats,
  };
};

export default useStudentData;
