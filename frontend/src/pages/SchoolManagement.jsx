import React, { useState } from 'react';
import { Box, Typography} from '@mui/material';
import ActionButtons from '../components/school_management/ActionButtons';
import FilterBar from '../components/school_management/FilterBar';
import ViewToggle from '../components/school_management/ViewToggle';
import SchoolTable from '../components/school_management/SchoolTable';
import useSchoolData from '../components/school_management/useSchoolData';

import Loader from '../components/utils/Loader';
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
        alert('Add New School functionality - To be implemented');
    };

    const handleImportSchools = () => {
        alert('Import Schools (CSV/Excel) functionality - To be implemented');
    };

    const handleExportSchoolList = () => {
        alert('Export School List functionality - To be implemented');
    };

    // Table action handlers
    const handleViewSchool = (school) => {
        console.log('View school:', school);
        alert(`View school: ${school.name}`);
    };

    const handleEditSchool = (school) => {
        console.log('Edit school:', school);
        alert(`Edit school: ${school.name}`);
    };

    const handleDeleteSchool = (school) => {
        console.log('Delete school:', school);
        if (window.confirm(`Are you sure you want to delete ${school.name}?`)) {
            alert(`Delete school: ${school.name}`);
        }
    };

    return (
        <Box sx={{ p: 3,  minHeight: '100vh' }}>
            {/* Header */}
            <Typography variant="h4" component="h1" sx={{ mb: 3, fontWeight: 600 }}>
                School Management
            </Typography>

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
                    Showing {filteredSchools.length} of {schools.length} schools
                </Typography>

                <ViewToggle
                    viewMode={viewMode}
                    onViewChange={setViewMode}
                />

            </Box>

            {/* Loading State */}
            {loading && <Loader message="Loading schools..." />}

            {!loading && viewMode === 'list' && (
                <SchoolTable
                    schools={filteredSchools}
                    onView={handleViewSchool}
                    onEdit={handleEditSchool}
                    onDelete={handleDeleteSchool}
                />
            )}

            {/* Map View */}
            {!loading && viewMode === 'map' && <MapView />}
        </Box>
    );
};

export default SchoolManagement;