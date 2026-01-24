import React, { useCallback, useState } from 'react';
import { Box, Snackbar, Alert, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Button as MuiButton, TablePagination, Select, MenuItem, FormControl, Typography } from '@mui/material';
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
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [teacherToDelete, setTeacherToDelete] = useState(null);
  
  // Pagination state
  const [page, setPage] = useState(0);
  const [rowsPerPage] = useState(20);  



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
  

// 1) Click trash icon -> open dialog
const handleDeleteTeacher = useCallback((teacher) => {
  setTeacherToDelete(teacher);
  setOpenDeleteDialog(true);
}, []);

// 2) Click "Löschen" in dialog -> call API
const handleConfirmDeleteTeacher = async () => {
  if (!teacherToDelete) return;

  try {
    await deleteTeacher(teacherToDelete.id);

    showNotification(
      `${teacherToDelete.first_name} ${teacherToDelete.last_name} wurde erfolgreich gelöscht`,
      'success'
    );
  } catch (error) {
    // show warning but still refresh (because it may be deleted anyway)
    console.error('Delete error:', error);
    showNotification(`Löschen: Backend meldet Fehler, ich lade neu...`, 'warning');
  } finally {
    setOpenDeleteDialog(false);
    setTeacherToDelete(null);
    await refetchTeachers();   // ✅ this is what removes it from the table
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
  }, [searchQuery, selectedProgram, selectedSchulamt]);

  // Paginate filtered teachers
  const paginatedTeachers = filteredTeachers.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  // Calculate total pages
  const totalPages = Math.ceil(filteredTeachers.length / rowsPerPage);

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
            <>
              <TeachersTable
                  teachers={paginatedTeachers}
                  onView={handleViewTeacher}
                  onEdit={handleEditTeacher}
                  onDelete={handleDeleteTeacher}
              />
              
              {/* Pagination Controls */}
              {filteredTeachers.length > 0 && (
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
                      {`${page * rowsPerPage + 1}-${Math.min((page + 1) * rowsPerPage, filteredTeachers.length)} von ${filteredTeachers.length}`}
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
                    count={filteredTeachers.length}
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
        <Dialog open={openDeleteDialog} onClose={() => setOpenDeleteDialog(false)}>
          <DialogTitle>Praktikumslehrkraft löschen</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Möchten Sie "{teacherToDelete?.first_name} {teacherToDelete?.last_name}" wirklich löschen?
              Diese Aktion kann nicht rückgängig gemacht werden.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <MuiButton onClick={() => { setOpenDeleteDialog(false); setTeacherToDelete(null); }}>
              Abbrechen
            </MuiButton>
            <MuiButton onClick={handleConfirmDeleteTeacher} color="error" variant="contained">
              Löschen
            </MuiButton>
          </DialogActions>
        </Dialog>

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