import React, { useCallback } from 'react';
import { Box } from '@mui/material';
import TeachersActionButtons from '../components/teachers/TeachersActionButtons';
import TeachersFilterBar from '../components/teachers/TeachersFilterBar';
import TeachersTable from '../components/teachers/TeachersTable';
import useTeacherData from '../components/teachers/useTeacherData';
import Loader from '../components/ui/Loader';

export default function Teachers() {
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
    alert('Neue Praktikumslehrkraft hinzufügen — Wird noch implementiert');
  }, []);

  const handleImport = useCallback(() => {
    alert('Praktikumslehrkräfte importieren (CSV/Excel) — Wird noch implementiert');
  }, []);

  const handleExport = useCallback(() => {
    alert('Praktikumslehrkräfte exportieren — Wird noch implementiert');
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
          {filteredTeachers.length} von {teachers.length} Praktikumslehrkräfte werden angezeigt • Verfügbar: {stats.available}
        </span>
      </Box>

      {loading && <Loader message="Praktikumslehrkräfte werden geladen..." />}

      {!loading && (
        <TeachersTable teachers={filteredTeachers} />
      )}
    </Box>
  );
}
