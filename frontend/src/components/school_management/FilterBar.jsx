import React from 'react';
import { Paper, Stack } from '@mui/material';
import SearchBar from './SearchBar';
import FilterSelect from './FilterSelect';

/**
 * Filter Bar Component
 * @param {Object} props
 * @param {string} props.searchQuery
 * @param {function} props.onSearchChange
 * @param {string} props.selectedDistrict
 * @param {function} props.onDistrictChange
 * @param {string[]} props.districts
 * @param {string} props.selectedType
 * @param {function} props.onTypeChange
 * @param {string[]} props.types
 * @param {string} props.selectedZone
 * @param {function} props.onZoneChange
 * @param {string[]} props.zones
 */
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
        <Paper sx={{ p: 2, mb: 2 }}>
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