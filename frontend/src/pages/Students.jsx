import React, { useCallback, useState, useEffect } from 'react';
import { Box, Snackbar, Alert, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Button as MuiButton, TablePagination, Select, MenuItem, FormControl, Typography } from '@mui/material';
import StudentsActionButtons from '../components/students/StudentsActionButtons';
import StudentsFilterBar from '../components/students/StudentsFilterBar';
import StudentsTable from '../components/students/StudentsTable';
import StudentFormDialog from '../components/students/StudentFormDialog';
import StudentViewDialog from '../components/students/StudentViewDialog';
import StudentAssignDialog from '../components/students/StudentAssignDialog';
import useStudentData from '../components/students/useStudentData';
import Loader from '../components/ui/Loader';
import Button from '../components/ui/Button';
import studentService from '../api/studentService';

export default function StudentsPage() {
  const {
    students,
    filteredStudents,
    loading,
    refetch,
    searchQuery, setSearchQuery,
    selectedProgram, setSelectedProgram,
    selectedRegion, setSelectedRegion,
    programs, regions,
    stats,
  } = useStudentData();

  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [hasAssignments, setHasAssignments] = useState(false);
  
  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [openViewDialog, setOpenViewDialog] = useState(false);
  const [openAssignDialog, setOpenAssignDialog] = useState(false);
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [openExportDialog, setOpenExportDialog] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState(null);
  
  // Pagination state
  const [page, setPage] = useState(0);
  const [rowsPerPage] = useState(20);

  useEffect(() => {
    const checkAssignments = async () => {
      try {
        const response = await studentService.checkAssignmentsStatus();
        setHasAssignments(response.data.has_assignments || false);
      } catch (error) {
        console.error('Error checking assignments status:', error);
        setHasAssignments(false);
      }
    };
    checkAssignments();
  }, []);

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
      const isNewStudent = !selectedStudent;
      setOpenAddDialog(false);
      setOpenEditDialog(false);
      setSelectedStudent(null);
      if (isNewStudent) {
        setSearchQuery('');
        setSelectedProgram('all');
        setSelectedRegion('all');
      }
      refetch();
      showNotification('Student erfolgreich gespeichert', 'success');
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

  const handleExport = useCallback(() => {
    setOpenExportDialog(true);
  }, []);

  const handleConfirmExport = async () => {
    setOpenExportDialog(false);
    
    try {
      const response = await studentService.exportExcel();

      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'students_export.xlsx';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      showNotification('Export erfolgreich', 'success');
    } catch (error) {
      showNotification(`Export fehlgeschlagen: ${error.message}`, 'error');
    }
  };

  // Pagination handlers
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handlePageJump = (event) => {
    setPage(event.target.value);
  };

  // Reset page when filters change
  React.useEffect(() => {
    setPage(0);
  }, [searchQuery, selectedProgram, selectedRegion]);

  // Paginate filtered students
  const paginatedStudents = filteredStudents.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  // Calculate total pages
  const totalPages = Math.ceil(filteredStudents.length / rowsPerPage);

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
        <>
          <StudentsTable 
            students={paginatedStudents}
            onView={handleViewStudent}
            onEdit={handleEditStudent}
            onAssign={handleAssignStudent}
            onDelete={handleDeleteStudent}
            canAssign={hasAssignments}
          />
          
          {/* Pagination Controls */}
          {filteredStudents.length > 0 && (
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between', 
              px: 2, 
              py: 2,
              mt: 2,
              backgroundColor: 'white',
              borderRadius: '12px',
              boxShadow: '0 2px 10px rgba(0, 0, 0, 0.08)'
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="body2" sx={{ color: '#6b7280' }}>
                  {`${page * rowsPerPage + 1}-${Math.min((page + 1) * rowsPerPage, filteredStudents.length)} von ${filteredStudents.length}`}
                </Typography>
                {totalPages > 1 && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2" sx={{ color: '#6b7280' }}>
                      Gehe zu Seite:
                    </Typography>
                    <FormControl size="small" sx={{ minWidth: 80 }}>
                      <Select
                        value={page}
                        onChange={handlePageJump}
                        sx={{ 
                          height: 32,
                          fontSize: '0.875rem',
                          '& .MuiOutlinedInput-notchedOutline': {
                            borderColor: '#d1d5db'
                          }
                        }}
                      >
                        {Array.from({ length: totalPages }, (_, i) => (
                          <MenuItem key={i} value={i}>
                            {i + 1}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Box>
                )}
              </Box>
              <TablePagination
                component="div"
                count={filteredStudents.length}
                page={page}
                onPageChange={handleChangePage}
                rowsPerPage={rowsPerPage}
                rowsPerPageOptions={[20]}
                labelDisplayedRows={() => ''}
                sx={{ 
                  border: 'none',
                  '& .MuiTablePagination-toolbar': {
                    minHeight: 'auto',
                    padding: 0
                  }
                }}
              />
            </Box>
          )}
        </>
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

      {/* Export Confirmation Dialog */}
      <Dialog open={openExportDialog} onClose={() => setOpenExportDialog(false)}>
        <DialogTitle>Studentenliste exportieren</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Möchten Sie die Studentenliste als Excel-Datei exportieren?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenExportDialog(false)} variant="secondary">
            Abbrechen
          </Button>
          <Button onClick={handleConfirmExport} variant="primary">
            Bestätigen
          </Button>
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
