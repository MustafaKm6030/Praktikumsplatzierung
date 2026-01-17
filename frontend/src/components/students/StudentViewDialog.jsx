import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Typography,
  Chip,
  Divider,
  Box,
} from '@mui/material';
import Button from '../ui/Button';

const StudentViewDialog = ({ open, onClose, student }) => {
  if (!student) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Typography variant="h6">
          Studentendetails: {student.first_name} {student.last_name}
        </Typography>
      </DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 2 }}>
          {/* Basic Information */}
          <Typography variant="subtitle1" color="primary" gutterBottom>
            Grundinformationen
          </Typography>
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">Studierenden-ID</Typography>
              <Typography variant="body1">{student.student_id || '—'}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">E-Mail</Typography>
              <Typography variant="body1">{student.email || '—'}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">Vorname</Typography>
              <Typography variant="body1">{student.first_name || '—'}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">Nachname</Typography>
              <Typography variant="body1">{student.last_name || '—'}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">Studiengang</Typography>
              <Chip 
                label={student.program === 'GS' ? 'Grundschule' : 'Mittelschule'} 
                color={student.program === 'GS' ? 'info' : 'warning'}
                size="small"
              />
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">Platzierungsstatus</Typography>
              <Chip 
                label={student.placement_status === 'PLACED' ? 'Zugewiesen' : 'Nicht zugewiesen'}
                color={student.placement_status === 'PLACED' ? 'success' : 'default'}
                size="small"
              />
            </Grid>
          </Grid>

          <Divider sx={{ my: 2 }} />

          {/* Subjects */}
          <Typography variant="subtitle1" color="primary" gutterBottom>
            Fächer
          </Typography>
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">Hauptfach</Typography>
              <Typography variant="body1">{student.primary_subject_name || '—'}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">Didaktikfach 1</Typography>
              <Typography variant="body1">{student.didactic_subject_1_name || '—'}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">Didaktikfach 2</Typography>
              <Typography variant="body1">{student.didactic_subject_2_name || '—'}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">Didaktikfach 3 (ZSP)</Typography>
              <Typography variant="body1">{student.didactic_subject_3_name || '—'}</Typography>
            </Grid>
          </Grid>

          <Divider sx={{ my: 2 }} />

          {/* Location */}
          <Typography variant="subtitle1" color="primary" gutterBottom>
            Standort
          </Typography>
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12}>
              <Typography variant="body2" color="text.secondary">Heimatadresse</Typography>
              <Typography variant="body1">{student.home_address || '—'}</Typography>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="body2" color="text.secondary">Semesteradresse</Typography>
              <Typography variant="body1">{student.semester_address || '—'}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">Region</Typography>
              <Typography variant="body1">{student.home_region || '—'}</Typography>
            </Grid>
          </Grid>

          <Divider sx={{ my: 2 }} />

          {/* Praktikum Completion Status */}
          <Typography variant="subtitle1" color="primary" gutterBottom>
            Praktikumsstatus
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">PDP I</Typography>
              <Typography variant="body1">{student.pdp1_completed_date || 'Nicht abgeschlossen'}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">PDP II</Typography>
              <Typography variant="body1">{student.pdp2_completed_date || 'Nicht abgeschlossen'}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">SFP</Typography>
              <Typography variant="body1">{student.sfp_completed_date || 'Nicht abgeschlossen'}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">ZSP</Typography>
              <Typography variant="body1">{student.zsp_completed_date || 'Nicht abgeschlossen'}</Typography>
            </Grid>
          </Grid>

          {student.notes && (
            <>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle1" color="primary" gutterBottom>
                Notizen
              </Typography>
              <Typography variant="body1">{student.notes}</Typography>
            </>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} variant="primary">Schließen</Button>
      </DialogActions>
    </Dialog>
  );
};

export default StudentViewDialog;
