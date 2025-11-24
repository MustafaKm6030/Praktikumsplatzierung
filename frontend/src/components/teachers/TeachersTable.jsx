import React from 'react';
import {
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Paper,
  Chip,
} from '@mui/material';

const TeachersTable = ({ teachers }) => {
  return (
    <TableContainer component={Paper} sx={{
      borderRadius: '12px',
      boxShadow: '0 2px 10px rgba(0, 0, 0, 0.08)',
      backgroundColor: 'white'
    }}>
      <Table>
        <TableHead>
          <TableRow sx={{ backgroundColor: '#fef9f3' }}>
            <TableCell><strong>PL ID</strong></TableCell>
            <TableCell><strong>Name</strong></TableCell>
            <TableCell><strong>School</strong></TableCell>
            <TableCell><strong>Program</strong></TableCell>
            <TableCell><strong>Preferred Praktika</strong></TableCell>
            <TableCell><strong>Credit Hrs (Anre-Std.)</strong></TableCell>
            <TableCell><strong>Capacity</strong></TableCell>
            <TableCell><strong>Schulamt</strong></TableCell>
            <TableCell><strong>Status</strong></TableCell>
          </TableRow>
        </TableHead>

        <TableBody>
          {(!teachers || teachers.length === 0) ? (
            <TableRow>
              <TableCell colSpan={10} align="center" sx={{ py: 8, color: 'text.secondary' }}>
                No PLs found matching your criteria
              </TableCell>
            </TableRow>
          ) : (
            teachers.map((pl) => (
              <TableRow key={pl.id} sx={{ '&:hover': { backgroundColor: '#f9f9f9' } }}>
                <TableCell>{`PL-${String(pl.id).padStart(3, '0')}`}</TableCell>
                <TableCell>{`${pl.first_name} ${pl.last_name}`}</TableCell>
                <TableCell>{pl.school_name || '—'}</TableCell>
                <TableCell>
                  <Chip
                    label={pl.program_display || pl.program}
                    size="small"
                    color={pl.program === 'GS' ? 'info' : 'warning'}
                  />
                </TableCell>
                {/* --- EDITED: Using the new raw field for simplicity --- */}
                <TableCell>{pl.preferred_praktika_raw || '—'}</TableCell>
                {/* --- EDITED: Using the correct field names --- */}
                <TableCell align="center">{pl.anrechnungsstunden}</TableCell>
                <TableCell align="center">{pl.capacity}</TableCell>
                <TableCell>{pl.schulamt || '—'}</TableCell>
                <TableCell>
                  {/* --- EDITED: Using is_active boolean --- */}
                  <Chip
                    label={pl.is_active ? 'Verfügbar' : 'Nicht verfügbar'}
                    color={pl.is_active ? 'success' : 'error'}
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default TeachersTable;
