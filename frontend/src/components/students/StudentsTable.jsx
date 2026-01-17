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
  IconButton,
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  AssignmentInd as AssignIcon,
} from '@mui/icons-material';

const StudentsTable = ({ students, onView, onEdit, onDelete, onAssign }) => {
  return (
    <TableContainer component={Paper} sx={{
      borderRadius: '12px',
      boxShadow: '0 2px 10px rgba(0, 0, 0, 0.08)',
      backgroundColor: 'white'
    }}>
      <Table>
        <TableHead>
          <TableRow sx={{ backgroundColor: '#fef9f3' }}>
            <TableCell><strong>Studierenden-ID</strong></TableCell>
            <TableCell><strong>Name</strong></TableCell>
            <TableCell><strong>Studiengang</strong></TableCell>
            <TableCell><strong>Hauptfach</strong></TableCell>
            <TableCell><strong>E-Mail</strong></TableCell>
            <TableCell><strong>Region</strong></TableCell>
            <TableCell><strong>Status</strong></TableCell>
            <TableCell align="center"><strong>Aktionen</strong></TableCell>
          </TableRow>
        </TableHead>

        <TableBody>
          {(!students || students.length === 0) ? (
            <TableRow>
              <TableCell colSpan={8} align="center" sx={{ py: 8, color: 'text.secondary' }}>
                Keine Studierenden gefunden, die Ihren Kriterien entsprechen
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
                    color={s.program === 'GS' ? 'info' : 'warning'}
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>{s.primary_subject_name || '—'}</TableCell>
                <TableCell>{s.email || '—'}</TableCell>
                <TableCell>{s.home_region || '—'}</TableCell>

                <TableCell>
                  <Chip
                    label={s.placement_status === 'PLACED' ? 'Zugewiesen' : 'Nicht zugewiesen'}
                    size="small"
                    color={s.placement_status === 'PLACED' ? 'success' : 'default'}
                  />
                </TableCell>
                <TableCell align="center">
                  <IconButton
                    size="small"
                    color="primary"
                    title="Details anzeigen"
                    onClick={() => onView && onView(s)}
                  >
                    <VisibilityIcon fontSize="small" />
                  </IconButton>
                  <IconButton
                    size="small"
                    color="primary"
                    title="Bearbeiten"
                    onClick={() => onEdit && onEdit(s)}
                  >
                    <EditIcon fontSize="small" />
                  </IconButton>
                  <IconButton
                    size="small"
                    color="secondary"
                    title="Zuweisen"
                    onClick={() => onAssign && onAssign(s)}
                  >
                    <AssignIcon fontSize="small" />
                  </IconButton>
                  <IconButton
                    size="small"
                    color="error"
                    title="Löschen"
                    onClick={() => onDelete && onDelete(s)}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default StudentsTable;