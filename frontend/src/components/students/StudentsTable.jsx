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

const StudentsTable = ({ students }) => {
  return (
    <TableContainer component={Paper} sx={{
      borderRadius: '12px',
      boxShadow: '0 2px 10px rgba(0, 0, 0, 0.08)',
      backgroundColor: 'white'
    }}>
      <Table>
        <TableHead>
          <TableRow sx={{ backgroundColor: '#fef9f3' }}>
            <TableCell><strong>Student ID</strong></TableCell>
            <TableCell><strong>Name</strong></TableCell>
            <TableCell><strong>Program</strong></TableCell>
            <TableCell><strong>Main Subject</strong></TableCell>
            <TableCell><strong>Additional Subjects</strong></TableCell>
            <TableCell><strong>Email</strong></TableCell>
            <TableCell><strong>Region</strong></TableCell>
            <TableCell><strong>Zone</strong></TableCell>
          </TableRow>
        </TableHead>

        <TableBody>
          {(!students || students.length === 0) ? (
            <TableRow>
              <TableCell colSpan={8} align="center" sx={{ py: 8, color: 'text.secondary' }}>
                No students found matching your criteria
              </TableCell>
            </TableRow>
          ) : (
            students.map((s) => (
              <TableRow key={s.id} sx={{ '&:hover': { backgroundColor: '#f9f9f9' } }}>
                <TableCell sx={{ fontWeight: 500 }}>{s.student_id || '—'}</TableCell>
                <TableCell>{[s.first_name, s.last_name].filter(Boolean).join(' ') || '—'}</TableCell>
                <TableCell>
                  <Chip
                    label={s.program === 'GS' ? 'Grundschule' : s.program === 'MS' ? 'Mittelschule' : (s.program || '—')}
                    size="small"
                    color={s.program === 'GS' ? 'info' : s.program === 'MS' ? 'warning' : 'default'}
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>{s.primary_subject_name || '—'}</TableCell>
                <TableCell>
                  {s.additional_subjects_names?.length ? s.additional_subjects_names.join(', ') : '—'}
                </TableCell>
                <TableCell>{s.email || '—'}</TableCell>
                <TableCell>{s.home_region || '—'}</TableCell>
                <TableCell>{s.preferred_zone || '—'}</TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default StudentsTable;
