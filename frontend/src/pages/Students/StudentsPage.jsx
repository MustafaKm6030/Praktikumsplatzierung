import React, { useCallback } from 'react';
import { Box } from '@mui/material';
import StudentsActionButtons from '../../components/students/StudentsActionButtons';
import StudentsFilterBar from '../../components/students/StudentsFilterBar';
import StudentsTable from '../../components/students/StudentsTable';
import useStudentData from '../../components/students/useStudentData';
import Loader from '../../components/utils/Loader';

export default function StudentsPage() {
  const {
    students,
    filteredStudents,
    loading,
    // filters
    searchQuery, setSearchQuery,
    selectedProgram, setSelectedProgram,
    selectedRegion, setSelectedRegion,
    programs, regions,
    // stats
    stats,
  } = useStudentData();

  // Actions (wire to your real service later if you want)
  const handleAddStudent = useCallback(() => {
    alert('Add New Student — to be implemented');
  }, []);

  const handleImport = useCallback(() => {
    // If you already have studentService.importCSV(file) you can add a hidden file input here.
    alert('Import Students (CSV/Excel) — to be implemented');
  }, []);

  const handleExport = useCallback(() => {
    // If you already have studentService.exportCSV(), call it here.
    alert('Export Students — to be implemented');
  }, []);

  return (
    <Box sx={{ p: 3, minHeight: '100vh', paddingTop: '5vh' }}>
      {/* Buttons (left, same as Schools) */}
      <StudentsActionButtons
        onAddStudent={handleAddStudent}
        onImport={handleImport}
        onExport={handleExport}
      />

      {/* Filters (one row, same pattern as Schools) */}
      <StudentsFilterBar
        searchQuery={searchQuery}
        onSearchChange={(e) => setSearchQuery(e.target.value)}
        selectedProgram={selectedProgram}
        onProgramChange={(e) => setSelectedProgram(e.target.value)}
        programs={programs}
        selectedRegion={selectedRegion}
        onRegionChange={(e) => setSelectedRegion(e.target.value)}
        regions={regions}
      />

      {/* Results summary (like Schools) */}
      <Box sx={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        mb: 2,
        flexWrap: 'wrap',
        gap: 2
      }}>
        <span style={{ color: '#6b7280', fontSize: 14 }}>
          Showing {filteredStudents.length} of {students.length} students
          {'  '}• GS: {stats.gs} • MS: {stats.ms}
        </span>
        {/* (If you later want a list/map toggle like Schools, add a ButtonGroup here) */}
      </Box>

      {loading && <Loader message="Loading students..." />}

      {!loading && (
        <StudentsTable students={filteredStudents} />
      )}
    </Box>
  );
}
