import React, { useState } from 'react';
import { Box, Typography } from '@mui/material';
import ActionButtons from '../components/school_management/ActionButtons';
import FilterBar from '../components/school_management/FilterBar';
import ViewToggle from '../components/school_management/ViewToggle';
import SchoolTable from '../components/school_management/SchoolTable';
import useSchoolData from '../components/school_management/useSchoolData';

import Loader from '../components/ui/Loader';
import MapView from "../components/school_management/MapView";

/**
 * Main School Management Component
 * This component orchestrates all child components and manages the overall state
 */
const SchoolManagement = () => {
    const [viewMode, setViewMode] = useState('list');

    // Use custom hook for data management
    const {
        schools,
        filteredSchools,
        loading,
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

    } = useSchoolData();

    // Action handlers
    const handleAddNewSchool = () => {
        alert('Neue Schule hinzufügen - Wird noch implementiert');
    };

    const handleImportSchools = () => {
        alert('Schulen importieren (CSV/Excel) - Wird noch implementiert');
    };

    const handleExportSchoolList = () => {
        alert('Schulliste exportieren - Wird noch implementiert');
    };

    // Table action handlers
    const handleViewSchool = (school) => {
        console.log('View school:', school);
        alert(`Schule anzeigen: ${school.name}`);
    };

    const handleEditSchool = (school) => {
        console.log('Edit school:', school);
        alert(`Schule bearbeiten: ${school.name}`);
    };

    const handleDeleteSchool = (school) => {
        console.log('Delete school:', school);
        if (window.confirm(`Möchten Sie wirklich ${school.name} löschen?`)) {
            alert(`Schule löschen: ${school.name}`);
        }
    };

    return (
        <Box sx={{ p: 3, minHeight: '100vh', paddingTop: '5vh' }}>
            {/* Action Buttons */}
            <ActionButtons
                onAddSchool={handleAddNewSchool}
                onImport={handleImportSchools}
                onExport={handleExportSchoolList}
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
            {loading && <Loader message="Schulen werden geladen..." />}

            {!loading && viewMode === 'list' && (
                <SchoolTable
                    schools={filteredSchools}
                    onView={handleViewSchool}
                    onEdit={handleEditSchool}
                    onDelete={handleDeleteSchool}
                />
            )}

            {/* Map View */}
            {!loading && viewMode === 'map' && <MapView schools={filteredSchools} />}
        </Box>
    );
};

export default SchoolManagement;