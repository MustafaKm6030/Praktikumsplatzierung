import React from 'react';
import { Paper, Stack } from '@mui/material';
import TextField from '../ui/TextField';
import Select from '../ui/Select';

const StudentsFilterBar = ({
  searchQuery,
  onSearchChange,
  selectedProgram,
  onProgramChange,
  programs,
  selectedRegion,
  onRegionChange,
  regions,
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
        <TextField
          value={searchQuery}
          onChange={onSearchChange}
          placeholder="Suche nach Name, ID oder E-Mail..."
        />

        <Select
          label="Studiengang"
          value={selectedProgram}
          onChange={onProgramChange}
          options={programs}
          fullWidth={false}
          minWidth={150}
        />

        <Select
          label="Region"
          value={selectedRegion}
          onChange={onRegionChange}
          options={regions}
          fullWidth={false}
          minWidth={150}
        />

        {/* Placeholder to visually match Schools (disabled extra filter) */}
        <Select
          label="Filter"
          value="all"
          onChange={() => {}}
          options={[]}
          disabled
          fullWidth={false}
          minWidth={150}
        />
      </Stack>
    </Paper>
  );
};

export default StudentsFilterBar;
