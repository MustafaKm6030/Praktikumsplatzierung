import React, { useState } from 'react';
import { Box, Snackbar, Alert } from '@mui/material';
import TeachersActionButtons from '../components/teachers/TeachersActionButtons';
import TeachersFilterBar from '../components/teachers/TeachersFilterBar';
import TeachersTable from '../components/teachers/TeachersTable';
import TeacherFormDialog from '../components/teachers/TeacherFormDialog';
import TeacherViewDialog from '../components/teachers/TeacherViewDialog';
import useTeacherData from '../components/teachers/useTeacherData';
import Loader from '../components/ui/Loader';
import { exportTeachersCSV, importTeachersCSV, deleteTeacher } from '../components/teachers/TeachersApi';

export default function Teachers() {
  const {
    teachers,
    filteredTeachers,
    loading,
    error,
    refetchTeachers,
    searchQuery, setSearchQuery,
    selectedProgram, setSelectedProgram,
    selectedSchulamt, setSelectedSchulamt,
    programOptions, schulamtOptions,
    stats,
  } = useTeacherData();

  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [openViewDialog, setOpenViewDialog] = useState(false);
  const [selectedTeacher, setSelectedTeacher] = useState(null);

  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  const showNotification = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleAddTeacher = () => {
    setSelectedTeacher(null);
    setOpenAddDialog(true);
  };

  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.xlsx,.xls';
    input.onchange = async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      const fileExtension = file.name.split('.').pop().toLowerCase();
      if (!['xlsx', 'xls'].includes(fileExtension)) {
        showNotification('Bitte wählen Sie eine Excel-Datei (.xlsx oder .xls)', 'error');
        return;
      }

      try {
        const result = await importTeachersCSV(file);
        showNotification(
            `Import erfolgreich: ${result.created} erstellt, ${result.updated} aktualisiert`,
            result.errors?.length > 0 ? 'warning' : 'success'
        );

        if (result.errors?.length > 0) {
          console.error('Import errors:', result.errors);
        }

        await refetchTeachers();
        
        setTimeout(() => {
          window.location.reload();
        }, 1500);
      } catch (error) {
        console.error('Import error:', error);
        showNotification(`Import fehlgeschlagen: ${error.message}`, 'error');
      }
    };
    input.click();
  };

  const handleExport = async () => {
    try {
      await exportTeachersCSV();
      showNotification('Praktikumslehrkräfte erfolgreich exportiert', 'success');
    } catch (error) {
      console.error('Export error:', error);
      showNotification(`Export fehlgeschlagen: ${error.message}`, 'error');
    }
  };

  const handleViewTeacher = (teacher) => {
    setSelectedTeacher(teacher);
    setOpenViewDialog(true);
  };

  const handleEditTeacher = (teacher) => {
    setSelectedTeacher(teacher);
    setOpenEditDialog(true);
  };

  const handleDeleteTeacher = async (teacher) => {
    if (window.confirm(`Möchten Sie wirklich ${teacher.first_name} ${teacher.last_name} löschen?`)) {
      try {
        await deleteTeacher(teacher.id);
        showNotification(`${teacher.first_name} ${teacher.last_name} wurde erfolgreich gelöscht`, 'success');
        await refetchTeachers();
      } catch (error) {
        console.error('Delete error:', error);
        showNotification(`Löschen fehlgeschlagen: ${error.message}`, 'error');
      }
    }
  };

  const handleTeacherSaved = async () => {
    setOpenAddDialog(false);
    setOpenEditDialog(false);
    setSelectedTeacher(null);
    await refetchTeachers();
    showNotification('Praktikumslehrkraft erfolgreich gespeichert', 'success');
  };

  const handleDialogClose = () => {
    setOpenAddDialog(false);
    setOpenEditDialog(false);
    setOpenViewDialog(false);
    setSelectedTeacher(null);
  };

  if (error) {
    return (
        <Box sx={{ p: 3, minHeight: '100vh', paddingTop: '5vh' }}>
          <Alert severity="error" sx={{ mb: 3 }}>
            Fehler beim Laden der Praktikumslehrkräfte: {error}
          </Alert>
        </Box>
    );
  }

  return (
      <Box sx={{ p: 3, minHeight: '100vh', paddingTop: '5vh' }}>
        <TeachersActionButtons
            onAddTeacher={handleAddTeacher}
            onImport={handleImport}
            onExport={handleExport}
        />

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

        {loading ? (
            <Loader message="Praktikumslehrkräfte werden geladen..." />
        ) : (
            <TeachersTable
                teachers={filteredTeachers}
                onView={handleViewTeacher}
                onEdit={handleEditTeacher}
                onDelete={handleDeleteTeacher}
            />
        )}

        <TeacherFormDialog
            open={openAddDialog}
            onClose={handleDialogClose}
            onSave={handleTeacherSaved}
            teacher={null}
            title="Neue Praktikumslehrkraft hinzufügen"
        />

        <TeacherFormDialog
            open={openEditDialog}
            onClose={handleDialogClose}
            onSave={handleTeacherSaved}
            teacher={selectedTeacher}
            title="Praktikumslehrkraft bearbeiten"
        />

        <TeacherViewDialog
            open={openViewDialog}
            onClose={handleDialogClose}
            teacher={selectedTeacher}
        />

        <Snackbar
            open={snackbar.open}
            autoHideDuration={6000}
            onClose={handleCloseSnackbar}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Box>
  );
}