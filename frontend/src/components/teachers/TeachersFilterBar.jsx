import React from 'react';
import { Paper, Stack } from '@mui/material';
import TextField from '../ui/TextField';
import Select from '../ui/Select';

const TeachersFilterBar = ({
  searchQuery,
  onSearchChange,
  selectedProgram,
  onProgramChange,
  programOptions,
  selectedSchulamt,
  onSchulamtChange,
  schulamtOptions,
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
          placeholder="Suche nach Name, E-Mail oder Schule..."
        />

        <Select
          label="Studiengang"
          value={selectedProgram}
          onChange={onProgramChange}
          options={programOptions}
          fullWidth={false}
          minWidth={150}
        />

        <Select
          label="Schulamt"
          value={selectedSchulamt}
          onChange={onSchulamtChange}
          options={schulamtOptions}
          fullWidth={false}
          minWidth={150}
        />
      </Stack>
    </Paper>
  );
};

export default TeachersFilterBar;
