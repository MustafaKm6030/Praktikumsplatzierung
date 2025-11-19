import { useState, useEffect, useCallback, useMemo } from 'react';
import studentService from '../api/studentService';
import { getErrorMessage } from '../api/config';

function buildStudentParams(filters) {
  const params = {};
  const searchValue = filters.search ? filters.search.trim() : '';

  if (searchValue) {
    params.search = searchValue;
  }

  if (filters.program) {
    params.program = filters.program;
  }

  if (filters.home_region) {
    params.home_region = filters.home_region;
  }

  return params;
}

async function loadStudentsList(filters, setStudents, setError, setLoading) {
  setLoading(true);
  setError(null);

  try {
    const params = buildStudentParams(filters);
    const response = await studentService.getAll(params);
    setStudents(response.data);
  } catch (err) {
    setError(getErrorMessage(err));
    // eslint-disable-next-line no-console
    console.error('Error fetching students:', err);
  } finally {
    setLoading(false);
  }
}

async function exportStudentsCSV(setError) {
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
    setError(getErrorMessage(err));
    // eslint-disable-next-line no-console
    console.error('Error exporting students:', err);
  }
}

async function importStudentsFromFile(event, setError, fetchStudents) {
  const input = event.target;
  const file = input && input.files ? input.files[0] : null;

  if (!file) {
    return;
  }

  try {
    await studentService.importCSV(file);
    await fetchStudents({});
  } catch (err) {
    setError(getErrorMessage(err));
    // eslint-disable-next-line no-console
    console.error('Error importing students:', err);
  } finally {
    input.value = '';
  }
}

function computeRegionOptions(students) {
  const uniqueRegions = [
    ...new Set(
      students
        .map((s) => s.home_region)
        .filter((region) => Boolean(region))
    ),
  ];

  return uniqueRegions.sort();
}

function computeStats(students) {
  return {
    total: students.length,
    gs: students.filter((s) => s.program === 'GS').length,
    ms: students.filter((s) => s.program === 'MS').length,
  };
}

function useStudentFetchCore() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStudents = useCallback(
    function fetchStudentsCallback(filters = {}) {
      loadStudentsList(filters, setStudents, setError, setLoading);
    },
    []
  );

  return {
    students,
    loading,
    error,
    fetchStudents,
    setError,
  };
}

function useInitialStudentFetch(fetchStudents) {
  useEffect(() => {
    fetchStudents({});
  }, [fetchStudents]);
}

function useStudentExportImport(fetchStudents, setError) {
  const onExport = useCallback(
    function onExportCallback() {
      exportStudentsCSV(setError);
    },
    [setError]
  );

  const onImport = useCallback(
    function onImportCallback(event) {
      importStudentsFromFile(event, setError, fetchStudents);
    },
    [fetchStudents, setError]
  );

  return {
    onExport,
    onImport,
  };
}

function filterStudentsList(students, searchTerm, programFilter, regionFilter) {
  let filtered = students;

  if (searchTerm) {
    const q = searchTerm.toLowerCase();
    filtered = filtered.filter(
      (s) =>
        (s.first_name && s.first_name.toLowerCase().includes(q)) ||
        (s.last_name && s.last_name.toLowerCase().includes(q)) ||
        (s.student_id && String(s.student_id).toLowerCase().includes(q)) ||
        (s.email && s.email.toLowerCase().includes(q))
    );
  }

  if (programFilter) {
    filtered = filtered.filter((s) => s.program === programFilter);
  }

  if (regionFilter) {
    filtered = filtered.filter((s) => s.home_region === regionFilter);
  }

  return filtered;
}

function useStudentFilterState(students, fetchStudents) {
  const [searchTerm, setSearchTermState] = useState('');
  const [programFilter, setProgramFilterState] = useState('');
  const [regionFilter, setRegionFilterState] = useState('');

  function onSearchChange(val) {
    setSearchTermState(val);
    fetchStudents({
      search: val,
      program: programFilter,
      home_region: regionFilter,
    });
  }

  function onProgramChange(val) {
    setProgramFilterState(val);
    fetchStudents({
      search: searchTerm,
      program: val,
      home_region: regionFilter,
    });
  }

  function onRegionChange(val) {
    setRegionFilterState(val);
    fetchStudents({
      search: searchTerm,
      program: programFilter,
      home_region: val,
    });
  }

  const regionOptions = useMemo(
    function regionOptionsMemo() {
      return computeRegionOptions(students);
    },
    [students]
  );

  const stats = useMemo(
    function statsMemo() {
      return computeStats(students);
    },
    [students]
  );

  return {
    searchTerm,
    programFilter,
    regionFilter,
    setSearchTerm: onSearchChange,
    setProgramFilter: onProgramChange,
    setRegionFilter: onRegionChange,
    regionOptions,
    stats,
  };
}

export default function useStudents() {
  const {
    students,
    loading,
    error,
    fetchStudents,
    setError,
  } = useStudentFetchCore();

  useInitialStudentFetch(fetchStudents);

  const { onExport, onImport } = useStudentExportImport(fetchStudents, setError);

  const filterState = useStudentFilterState(students, fetchStudents);

  return {
    students,
    loading,
    error,
    onExport,
    onImport,
    ...filterState,
  };
}
