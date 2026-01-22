import React, { useState } from 'react';
import { Box, Typography, Snackbar, Alert } from '@mui/material';
import ActionButtons from '../components/school_management/ActionButtons';
import FilterBar from '../components/school_management/FilterBar';
import ViewToggle from '../components/school_management/ViewToggle';
import SchoolTable from '../components/school_management/SchoolTable';
import useSchoolData from '../components/school_management/useSchoolData';
import SchoolFormDialog from '../components/school_management/SchoolFormDialog';
import SchoolViewDialog from '../components/school_management/SchoolViewDialog';
import Loader from '../components/ui/Loader';
import MapView from "../components/school_management/MapView";
import { exportSchoolsExcel, importSchoolsCSV, deleteSchool, runGeocodingTask } from '../components/school_management/SchoolsApi';

/**
 * Main School Management Component
 */
const SchoolManagement = () => {
    const [viewMode, setViewMode] = useState('list');
    const [openAddDialog, setOpenAddDialog] = useState(false);
    const [openEditDialog, setOpenEditDialog] = useState(false);
    const [openViewDialog, setOpenViewDialog] = useState(false);
    const [selectedSchool, setSelectedSchool] = useState(null);
    const [isGeocoding, setIsGeocoding] = useState(false);
    // Snackbar for notifications
    const [snackbar, setSnackbar] = useState({
        open: false,
        message: '',
        severity: 'success'
    });

    // Use custom hook for data management
    const {
        schools,
        filteredSchools,
        loading,
        error,
        searchQuery,
        setSearchQuery,
        selectedDistrict,
        setSelectedDistrict,
        selectedType,
        setSelectedType,
        selectedZone,
        setSelectedZone,
        districts,
        types,
        zones,
        fetchSchools: refetchSchools,
    } = useSchoolData();

    // Show notification
    const showNotification = (message, severity = 'success') => {
        setSnackbar({ open: true, message, severity });
    };

    // Close notification
    const handleCloseSnackbar = () => {
        setSnackbar({ ...snackbar, open: false });
    };

    // Action handlers
    const handleAddNewSchool = () => {
        setSelectedSchool(null);
        setOpenAddDialog(true);
    };

    const handleImportSchools = () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.csv';
        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            try {
                const result = await importSchoolsCSV(file);
                showNotification(
                    `Import erfolgreich: ${result.created} erstellt, ${result.updated} aktualisiert`,
                    result.errors?.length > 0 ? 'warning' : 'success'
                );

                if (result.errors?.length > 0) {
                    console.error('Import errors:', result.errors);
                }

                await refetchSchools();
            } catch (error) {
                console.error('Import error:', error);
                showNotification(`Import fehlgeschlagen: ${error.message}`, 'error');
            }
            e.target.value = '';
        };
        input.click();
    };

    const handleExportSchoolList = async () => {
        try {
            await exportSchoolsExcel();
            showNotification('Schulliste erfolgreich exportiert', 'success');
        } catch (error) {
            console.error('Export error:', error);
            const msg = error.message || "Excel-Export fehlgeschlagen";
            showNotification(msg, 'error');
        }
    };


    // Table action handlers
    const handleViewSchool = (school) => {
        setSelectedSchool(school);
        setOpenViewDialog(true);
    };

    const handleEditSchool = (school) => {
        setSelectedSchool(school);
        setOpenEditDialog(true);
    };

    const handleRunGeocoding = async () => {
        if (window.confirm("Dieser Prozess kann mehrere Minuten dauern. Die Seite wird blockiert, bis der Vorgang abgeschlossen ist. Möchten Sie fortfahren?")) {
            setIsGeocoding(true);

            try {
                const result = await runGeocodingTask();
                const { success, failed, connection_error } = result.stats || {};
                
                if (connection_error) {
                    showNotification(`Geocoding wurde aufgrund eines Verbindungsfehlers gestoppt. Erfolgreich: ${success || 0}, Fehlgeschlagen: ${failed || 0}.`, "warning");
                } else {
                    showNotification(`Geocoding abgeschlossen! Erfolgreich: ${success || 0}, Fehlgeschlagen: ${failed || 0}.`, "success");
                }
                await refetchSchools();
            } catch (error) {
                console.error('Geocoding error:', error);
                if (error.connectionError && error.stats) {
                    const { success, failed } = error.stats;
                    showNotification(`Verbindungsfehler: Geocoding gestoppt. Erfolgreich: ${success || 0}, Fehlgeschlagen: ${failed || 0}.`, "warning");
                } else {
                    const errorMessage = error.message.includes('Connection') || error.message.includes('Verbindung') 
                        ? `Verbindungsfehler beim Geocoding: ${error.message}` 
                        : `Fehler beim Geocoding: ${error.message}`;
                    showNotification(errorMessage, 'error');
                }
                await refetchSchools();
            } finally {
                setIsGeocoding(false);
            }
        }
    };
    const handleDeleteSchool = async (school) => {
        if (window.confirm(`Möchten Sie wirklich ${school.name} löschen?`)) {
            try {
                await deleteSchool(school.id);
                showNotification(`${school.name} wurde erfolgreich gelöscht`, 'success');
                await refetchSchools();
            } catch (error) {
                console.error('Delete error:', error);
                showNotification(`Löschen fehlgeschlagen: ${error.message}`, 'error');
            }
        }
    };

    // Dialog handlers
    const handleSchoolSaved = async () => {
        setOpenAddDialog(false);
        setOpenEditDialog(false);
        setSelectedSchool(null);
        await refetchSchools();
        showNotification('Schule erfolgreich gespeichert', 'success');
    };

    const handleDialogClose = () => {
        setOpenAddDialog(false);
        setOpenEditDialog(false);
        setOpenViewDialog(false);
        setSelectedSchool(null);
    };

    // Show error message if API fails
    if (error) {
        return (
            <Box sx={{ p: 3, minHeight: '100vh', paddingTop: '5vh' }}>
                <Alert severity="error" sx={{ mb: 3 }}>
                    Fehler beim Laden der Schulen: {error}
                </Alert>
            </Box>
        );
    }

    return (
        <Box sx={{ p: 3, minHeight: '100vh', paddingTop: '5vh' }}>
            {/* Action Buttons */}
            <ActionButtons
                onAddSchool={handleAddNewSchool}
                onImport={handleImportSchools}
                onExport={handleExportSchoolList}
                onGeocode={handleRunGeocoding}
                isGeocoding={isGeocoding}
            />

            {/* Filter Bar */}
            <FilterBar
                searchQuery={searchQuery}
                onSearchChange={(e) => setSearchQuery(e.target.value)}
                selectedDistrict={selectedDistrict}
                onDistrictChange={(e) => setSelectedDistrict(e.target.value)}
                districts={districts}
                selectedType={selectedType}
                onTypeChange={(e) => setSelectedType(e.target.value)}
                types={types}
                selectedZone={selectedZone}
                onZoneChange={(e) => setSelectedZone(e.target.value)}
                zones={zones}
            />

            {/* Results Bar */}
            <Box sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                mb: 2,
                flexWrap: 'wrap',
                gap: 2
            }}>
                <Typography variant="body2" color="text.secondary">
                    {filteredSchools.length} von {schools.length} Schulen werden angezeigt
                </Typography>

                <ViewToggle
                    viewMode={viewMode}
                    onViewChange={setViewMode}
                />
            </Box>

            {/* Loading State */}
            {loading || isGeocoding ? (
                <Loader message={isGeocoding ? "Geocoding schools... This may take several minutes." : "Loading schools..."} />
            ) : (
                <>
                    {/* Table View */}
                    {viewMode === 'list' && (
                        <SchoolTable
                            schools={filteredSchools}
                            onView={handleViewSchool}
                            onEdit={handleEditSchool}
                            onDelete={handleDeleteSchool}
                        />
                    )}

                    {/* Map View */}
                    {viewMode === 'map' && <MapView schools={filteredSchools} />}
                </>
            )}

            {/* Add School Dialog */}
            <SchoolFormDialog
                open={openAddDialog}
                onClose={handleDialogClose}
                onSave={handleSchoolSaved}
                school={null}
                title="Neue Schule hinzufügen"
            />

            {/* Edit School Dialog */}
            <SchoolFormDialog
                open={openEditDialog}
                onClose={handleDialogClose}
                onSave={handleSchoolSaved}
                school={selectedSchool}
                title="Schule bearbeiten"
            />

            {/* View School Dialog */}
            <SchoolViewDialog
                open={openViewDialog}
                onClose={handleDialogClose}
                school={selectedSchool}
            />

            {/* Notification Snackbar */}
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
};

export default SchoolManagement;