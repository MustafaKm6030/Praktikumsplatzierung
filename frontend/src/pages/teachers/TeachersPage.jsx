import React, { useCallback } from 'react';
import { Box } from '@mui/material';
import TeachersActionButtons from '../../components/teachers/TeachersActionButtons';
import TeachersFilterBar from '../../components/teachers/TeachersFilterBar';
import TeachersTable from '../../components/teachers/TeachersTable';
import useTeacherData from '../../components/teachers/useTeacherData';
import Loader from '../../components/utils/Loader';

export default function TeachersPage() {
  const {
    teachers,
    filteredTeachers,
    loading,
    // filters
    searchQuery, setSearchQuery,
    selectedProgram, setSelectedProgram,
    selectedSchulamt, setSelectedSchulamt,
    programOptions, schulamtOptions,
    // stats
    stats,
  } = useTeacherData();

  // Actions (wire to your plService later)
  const handleAddTeacher = useCallback(() => {
    alert('Add New PL — to be implemented');
  }, []);

  const handleImport = useCallback(() => {
    alert('Import PLs (CSV/Excel) — to be implemented');
  }, []);

  const handleExport = useCallback(() => {
    alert('Export PL list — to be implemented');
  }, []);

  return (
    <Box sx={{ p: 3, minHeight: '100vh', paddingTop: '5vh' }}>
      {/* Buttons (left, same as Schools) */}
      <TeachersActionButtons
        onAddTeacher={handleAddTeacher}
        onImport={handleImport}
        onExport={handleExport}
      />

      {/* Filters (one row, same pattern as Schools) */}
      <TeachersFilterBar
        searchQuery={searchQuery}
        onSearchChange={(e) => setSearchQuery(e.target.value)}
        selectedProgram={selectedProgram}
        onProgramChange={(e) => setSelectedProgram(e.target.value)}
        programOptions={programOptions}
        selectedSchulamt={selectedSchulamt}
        onSchulamtChange={(e) => setSelectedSchulamt(e.target.value)}
        schulamtOptions={schulamtOptions}
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
          Showing {filteredTeachers.length} of {teachers.length} PLs • Available: {stats.available}
        </span>
      </Box>

      {loading && <Loader message="Loading PLs..." />}

      {!loading && (
        <TeachersTable teachers={filteredTeachers} />
      )}
    </Box>
  );
}
