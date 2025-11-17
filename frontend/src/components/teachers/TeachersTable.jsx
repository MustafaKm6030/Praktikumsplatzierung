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
            <TableCell><strong>Main Subject</strong></TableCell>
            <TableCell><strong>Preferred Praktika</strong></TableCell>
            <TableCell><strong>Credit Hrs</strong></TableCell>
            <TableCell><strong>Schulamt</strong></TableCell>
            <TableCell><strong>Max Students</strong></TableCell>
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
            teachers.map((pl) => {
              const programLabel =
                pl.program === 'GS' ? 'Grundschule' :
                pl.program === 'MS' ? 'Mittelschule' :
                (pl.program_display || pl.program || '—');

              const praktika = (pl.available_praktikum_types || []).map((pt) => {
                if (typeof pt === 'object' && (pt.name || pt.code)) return pt.name || pt.code;
                return String(pt);
              });

              return (
                <TableRow key={pl.id} sx={{ '&:hover': { backgroundColor: '#f9f9f9' } }}>
                  <TableCell sx={{ fontWeight: 500 }}>
                    {`PL-${String(pl.id ?? '').padStart(3, '0')}`}
                  </TableCell>

                  <TableCell>
                    {[pl.first_name, pl.last_name].filter(Boolean).join(' ') || '—'}
                  </TableCell>

                  <TableCell>{pl.school_name || '—'}</TableCell>

                  <TableCell>
                    <Chip
                      label={programLabel}
                      size="small"
                      color={pl.program === 'GS' ? 'info' : pl.program === 'MS' ? 'warning' : 'default'}
                      variant="outlined"
                    />
                  </TableCell>

                  <TableCell>{pl.main_subject_name || '—'}</TableCell>

                  <TableCell>
                    {praktika.length ? praktika.join(', ') : '—'}
                  </TableCell>

                  <TableCell align="center">
                    {pl.max_simultaneous_praktikum ?? 2}
                  </TableCell>

                  <TableCell>
                    {pl.schulamt || '—'}
                  </TableCell>

                  <TableCell align="center">
                    {pl.max_students_per_praktikum ?? 3}
                  </TableCell>

                  <TableCell>
                    <Chip
                      label={pl.is_available ? 'Verfügbar' : 'Nicht verfügbar'}
                      color={pl.is_available ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                </TableRow>
              );
            })
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default TeachersTable;
