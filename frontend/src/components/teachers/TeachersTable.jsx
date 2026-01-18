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
} from '@mui/icons-material';

const TeachersTable = ({ teachers, onView, onEdit, onDelete }) => {
  return (
      <TableContainer component={Paper} sx={{
        borderRadius: '12px',
        boxShadow: '0 2px 10px rgba(0, 0, 0, 0.08)',
        backgroundColor: 'white'
      }}>
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: '#fef9f3' }}>
              <TableCell><strong>PL-ID</strong></TableCell>
              <TableCell><strong>Name</strong></TableCell>
              <TableCell><strong>Schule</strong></TableCell>
              <TableCell><strong>Studiengang</strong></TableCell>
              <TableCell><strong>Bevorzugte Praktika</strong></TableCell>
              <TableCell><strong>Anrechnungsstunden</strong></TableCell>
              <TableCell><strong>Kapazität</strong></TableCell>
              <TableCell><strong>Schulamt</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
              <TableCell align="center"><strong>Aktionen</strong></TableCell>
            </TableRow>
          </TableHead>

          <TableBody>
            {(!teachers || teachers.length === 0) ? (
                <TableRow>
                  <TableCell colSpan={10} align="center" sx={{ py: 8, color: 'text.secondary' }}>
                    Keine Praktikumslehrkräfte gefunden, die Ihren Kriterien entsprechen
                  </TableCell>
                </TableRow>
            ) : (
                teachers.map((pl) => (
                    <TableRow key={pl.id} sx={{ '&:hover': { backgroundColor: '#f9f9f9' } }}>
                      <TableCell>{`PL-${String(pl.pl_id ?? pl.teacher_id ?? pl.praktikumslehrkraft_id ?? pl.id).padStart(3, '0')}`}</TableCell>
                      <TableCell sx={{ fontWeight: 500 }}>{`${pl.first_name} ${pl.last_name}`}</TableCell>
                      <TableCell>{pl.school_name || '—'}</TableCell>
                      <TableCell>
                        <Chip
                            label={pl.program_display || pl.program}
                            size="small"
                            color={pl.program === 'GS' ? 'info' : 'warning'}
                        />
                      </TableCell>
                      <TableCell>{pl.preferred_praktika_raw || '—'}</TableCell>
                      <TableCell align="center">{pl.anrechnungsstunden || 0}</TableCell>
                      <TableCell align="center">{pl.capacity || 0}</TableCell>
                      <TableCell>{pl.schulamt || '—'}</TableCell>
                      <TableCell>
                        <Chip
                            label={pl.is_active ? 'Verfügbar' : 'Nicht verfügbar'}
                            color={pl.is_active ? 'success' : 'error'}
                            size="small"
                        />
                      </TableCell>
                      <TableCell align="center">
                        <IconButton
                            size="small"
                            color="primary"
                            title="Details anzeigen"
                            onClick={() => onView && onView(pl)}
                        >
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                        <IconButton
                            size="small"
                            color="primary"
                            title="Bearbeiten"
                            onClick={() => onEdit && onEdit(pl)}
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                        <IconButton
                            size="small"
                            color="error"
                            title="Löschen"
                            onClick={() => onDelete && onDelete(pl)}
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

export default TeachersTable;