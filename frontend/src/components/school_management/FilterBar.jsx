import React from 'react';
import { Paper, Stack } from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import TextField from '../ui/TextField';
import Select from '../ui/Select';

const FilterBar = ({
                       searchQuery,
                       onSearchChange,
                       selectedDistrict,
                       onDistrictChange,
                       districts,
                       selectedType,
                       onTypeChange,
                       types,
                       selectedZone,
                       onZoneChange,
                       zones,
                   }) => {
    return (
        <Paper sx={{
            p: 2,
            mb: 2,
            borderRadius: '16px',
            backgroundColor: 'white',
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.08)',
            border: '1px solid rgba(248, 151, 28, 0.15)'
        }}>
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
                {/* Replaced SearchBar component with direct TextField usage */}
                <TextField
                    value={searchQuery}
                    onChange={onSearchChange}
                    placeholder="Search by School Name, District, City..."
                    fullWidth
                    startIcon={<SearchIcon sx={{ color: '#6b7280' }} />}
                />

                <Select
                    label="District"
                    value={selectedDistrict}
                    onChange={onDistrictChange}
                    options={districts}
                    fullWidth={false}
                    minWidth={150}
                />

                <Select
                    label="Type"
                    value={selectedType}
                    onChange={onTypeChange}
                    options={types}
                    fullWidth={false}
                    minWidth={150}
                />

                <Select
                    label="Zone"
                    value={selectedZone}
                    onChange={onZoneChange}
                    options={zones}
                    fullWidth={false}
                    minWidth={150}
                />
            </Stack>
        </Paper>
    );
};

export default FilterBar;