import React, { useCallback, useState } from 'react';
import { Box, Snackbar, Alert, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Button as MuiButton } from '@mui/material';
import StudentsActionButtons from '../components/students/StudentsActionButtons';
import StudentsFilterBar from '../components/students/StudentsFilterBar';
import StudentsTable from '../components/students/StudentsTable';
import StudentFormDialog from '../components/students/StudentFormDialog';
import StudentViewDialog from '../components/students/StudentViewDialog';
import StudentAssignDialog from '../components/students/StudentAssignDialog';
import useStudentData from '../components/students/useStudentData';
import Loader from '../components/ui/Loader';
import studentService from '../api/studentService';

export default function StudentsPage() {
  const {
    students,
    filteredStudents,
    loading,
    refetch,
    // filters
    searchQuery, setSearchQuery,
    selectedProgram, setSelectedProgram,
    selectedRegion, setSelectedRegion,
    programs, regions,
    // stats
    stats,
  } = useStudentData();

  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  
  // Dialog states
  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [openViewDialog, setOpenViewDialog] = useState(false);
  const [openAssignDialog, setOpenAssignDialog] = useState(false);
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState(null);

  const showNotification = (message, severity = 'success') => {
    setNotification({ open: true, message, severity });
  };

  const handleAddStudent = useCallback(() => {
    setSelectedStudent(null);
    setOpenAddDialog(true);
  }, []);

  const handleViewStudent = useCallback((student) => {
    setSelectedStudent(student);
    setOpenViewDialog(true);
  }, []);

  const handleEditStudent = useCallback((student) => {
    setSelectedStudent(student);
    setOpenEditDialog(true);
  }, []);

  const handleAssignStudent = useCallback((student) => {
    setSelectedStudent(student);
    setOpenAssignDialog(true);
  }, []);

  const handleDeleteStudent = useCallback((student) => {
    setSelectedStudent(student);
    setOpenDeleteDialog(true);
  }, []);

  const handleSaveStudent = async () => {
    try {
      showNotification('Student erfolgreich gespeichert', 'success');
      setOpenAddDialog(false);
      setOpenEditDialog(false);
      setSelectedStudent(null);
      refetch();
    } catch (error) {
      showNotification(`Fehler: ${error.message}`, 'error');
    }
  };

  const handleConfirmDelete = async () => {
    try {
      await studentService.delete(selectedStudent.id);
      showNotification('Student erfolgreich gelöscht', 'success');
      setOpenDeleteDialog(false);
      setSelectedStudent(null);
      refetch();
    } catch (error) {
      showNotification(`Fehler beim Löschen: ${error.message}`, 'error');
    }
  };

  const handleSaveAssignment = async () => {
    try {
      showNotification('Student erfolgreich zugewiesen', 'success');
      setOpenAssignDialog(false);
      setSelectedStudent(null);
      refetch();
    } catch (error) {
      showNotification(`Fehler bei der Zuweisung: ${error.message}`, 'error');
    }
  };

  const handleImport = useCallback(() => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.csv,.xlsx';
    input.onchange = async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      try {
        const isExcel = file.name.endsWith('.xlsx');
        const result = isExcel 
          ? await studentService.importExcel(file)
          : await studentService.importCSV(file);
        
        const data = result.data;
        showNotification(
          `Import erfolgreich: ${data.created} erstellt, ${data.updated} aktualisiert${data.errors?.length ? `, ${data.errors.length} Fehler` : ''}`,
          data.errors?.length ? 'warning' : 'success'
        );
        refetch();
      } catch (error) {
        showNotification(`Import fehlgeschlagen: ${error.message}`, 'error');
      }
    };
    input.click();
  }, [refetch]);

  const handleExport = useCallback(async () => {
    try {
      // Show menu to choose format
      const format = window.confirm('Excel exportieren? (OK = Excel, Abbrechen = CSV)')
        ? 'excel'
        : 'csv';

      const response = format === 'excel'
        ? await studentService.exportExcel()
        : await studentService.exportCSV();

      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `students_export.${format === 'excel' ? 'xlsx' : 'csv'}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      showNotification('Export erfolgreich', 'success');
    } catch (error) {
      showNotification(`Export fehlgeschlagen: ${error.message}`, 'error');
    }
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
          {filteredStudents.length} von {students.length} Studierende werden angezeigt
          {'  '}• GS: {stats.gs} • MS: {stats.ms}
        </span>
        {/* (If you later want a list/map toggle like Schools, add a ButtonGroup here) */}
      </Box>

      {loading && <Loader message="Studierende werden geladen..." />}

      {!loading && (
        <StudentsTable 
          students={filteredStudents}
          onView={handleViewStudent}
          onEdit={handleEditStudent}
          onAssign={handleAssignStudent}
          onDelete={handleDeleteStudent}
        />
      )}

      {/* Add Student Dialog */}
      <StudentFormDialog
        open={openAddDialog}
        onClose={() => setOpenAddDialog(false)}
        onSave={handleSaveStudent}
        student={null}
      />

      {/* Edit Student Dialog */}
      <StudentFormDialog
        open={openEditDialog}
        onClose={() => setOpenEditDialog(false)}
        onSave={handleSaveStudent}
        student={selectedStudent}
      />

      {/* View Student Dialog */}
      <StudentViewDialog
        open={openViewDialog}
        onClose={() => setOpenViewDialog(false)}
        student={selectedStudent}
      />

      {/* Assign Student Dialog */}
      <StudentAssignDialog
        open={openAssignDialog}
        onClose={() => setOpenAssignDialog(false)}
        onSave={handleSaveAssignment}
        student={selectedStudent}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={openDeleteDialog} onClose={() => setOpenDeleteDialog(false)}>
        <DialogTitle>Student löschen</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Möchten Sie den Studenten "{selectedStudent?.first_name} {selectedStudent?.last_name}" wirklich löschen?
            Diese Aktion kann nicht rückgängig gemacht werden.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <MuiButton onClick={() => setOpenDeleteDialog(false)}>Abbrechen</MuiButton>
          <MuiButton onClick={handleConfirmDelete} color="error" variant="contained">
            Löschen
          </MuiButton>
        </DialogActions>
      </Dialog>

      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification({ ...notification, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert severity={notification.severity} onClose={() => setNotification({ ...notification, open: false })}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
