import React from 'react';
import { Paper, Stack } from '@mui/material';
import SearchBar from './SearchBar';
import FilterSelect from './FilterSelect';

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
                <SearchBar
                    value={searchQuery}
                    onChange={onSearchChange}
                    placeholder="Search by School Name, District, City..."
                />

                <FilterSelect
                    label="District"
                    value={selectedDistrict}
                    onChange={onDistrictChange}
                    options={districts}
                />

                <FilterSelect
                    label="Type"
                    value={selectedType}
                    onChange={onTypeChange}
                    options={types}
                />

                <FilterSelect
                    label="Zone"
                    value={selectedZone}
                    onChange={onZoneChange}
                    options={zones}
                />

                <FilterSelect
                    label="Filter"
                    value="all"
                    onChange={() => {}}
                    options={[]}
                    disabled
                />
            </Stack>
        </Paper>
    );
};

export default FilterBar;