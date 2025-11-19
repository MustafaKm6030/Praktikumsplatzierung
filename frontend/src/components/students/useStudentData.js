import { useState, useEffect, useCallback, useMemo } from 'react';

/**
 * Student type (reference)
 * {
 *   id, student_id, first_name, last_name,
 *   program ('GS'|'MS'), primary_subject_name, additional_subjects_names[],
 *   email, home_region, preferred_zone
 * }
 */

async function requestStudents() {
  const res = await fetch('/api/students');

  if (!res.ok) {
    // eslint-disable-next-line no-console
    console.error('Failed to fetch students:', res.status, res.statusText);
    return [];
  }

  const data = await res.json();
  return data || [];
}

function collectRegions(data) {
  const uniqueRegions = [
    ...new Set(
      data
        .map((s) => s.home_region)
        .filter((region) => Boolean(region))
    ),
  ];
  return uniqueRegions;
}

async function loadStudentData(setStudents, setLoading, setPrograms, setRegions) {
  setLoading(true);
  try {
    const list = await requestStudents();
    setStudents(list);
    setPrograms(['GS', 'MS']);
    setRegions(collectRegions(list));
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('Error fetching students:', err);
  } finally {
    setLoading(false);
  }
}

function filterStudentsBySearch(students, searchQuery) {
  if (!searchQuery) {
    return students;
  }

  const q = searchQuery.toLowerCase();

  return students.filter(
    (s) =>
      (s.first_name && s.first_name.toLowerCase().includes(q)) ||
      (s.last_name && s.last_name.toLowerCase().includes(q)) ||
      (s.student_id && String(s.student_id).toLowerCase().includes(q)) ||
      (s.email && s.email.toLowerCase().includes(q))
  );
}

function filterStudentsByProgram(students, selectedProgram) {
  if (selectedProgram === 'all') {
    return students;
  }

  return students.filter((s) => s.program === selectedProgram);
}

function filterStudentsByRegion(students, selectedRegion) {
  if (selectedRegion === 'all') {
    return students;
  }

  return students.filter((s) => s.home_region === selectedRegion);
}

function computeStats(students) {
  const gs = students.filter((s) => s.program === 'GS').length;
  const ms = students.filter((s) => s.program === 'MS').length;
  return { gs, ms };
}

function useStudentBaseCore() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [programs, setPrograms] = useState(['GS', 'MS']);
  const [regions, setRegions] = useState([]);

  const fetchStudents = useCallback(
    function fetchStudentsCallback() {
      loadStudentData(setStudents, setLoading, setPrograms, setRegions);
    },
    []
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
    let result = students;

    result = filterStudentsBySearch(result, searchQuery);
    result = filterStudentsByProgram(result, selectedProgram);
    result = filterStudentsByRegion(result, selectedRegion);

    setFilteredStudents(result);
  }, [searchQuery, selectedProgram, selectedRegion, students]);

  const stats = useMemo(
    function statsMemo() {
      return computeStats(students);
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
  const base = useStudentBaseCore();
  const filters = useStudentFilters(base.students);

  return {
    students: base.students,
    filteredStudents: filters.filteredStudents,
    loading: base.loading,
    searchQuery: filters.searchQuery,
    setSearchQuery: filters.setSearchQuery,
    selectedProgram: filters.selectedProgram,
    setSelectedProgram: filters.setSelectedProgram,
    selectedRegion: filters.selectedRegion,
    setSelectedRegion: filters.setSelectedRegion,
    programs: base.programs,
    regions: base.regions,
    stats: filters.stats,
  };
};

export default useStudentData;
