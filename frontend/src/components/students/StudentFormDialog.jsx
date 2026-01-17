import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Typography,
} from '@mui/material';
import Button from '../ui/Button';
import TextField from '../ui/TextField';
import Select from '../ui/Select';
import studentService from '../../api/studentService';

const StudentFormDialog = ({ open, onClose, onSave, student }) => {
  const [formData, setFormData] = useState({
    student_id: '',
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    program: 'GS',
    home_address: '',
    semester_address: '',
    home_region: '',
    placement_status: 'UNPLACED',
    notes: '',
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (student) {
      setFormData({
        student_id: student.student_id || '',
        first_name: student.first_name || '',
        last_name: student.last_name || '',
        email: student.email || '',
        phone: student.phone || '',
        program: student.program || 'GS',
        home_address: student.home_address || '',
        semester_address: student.semester_address || '',
        home_region: student.home_region || '',
        placement_status: student.placement_status || 'UNPLACED',
        notes: student.notes || '',
      });
    } else {
      setFormData({
        student_id: '',
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        program: 'GS',
        home_address: '',
        semester_address: '',
        home_region: '',
        placement_status: 'UNPLACED',
        notes: '',
      });
    }
    setErrors({});
  }, [student, open]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.student_id.trim()) newErrors.student_id = 'Studierenden-ID ist erforderlich';
    if (!formData.first_name.trim()) newErrors.first_name = 'Vorname ist erforderlich';
    if (!formData.last_name.trim()) newErrors.last_name = 'Nachname ist erforderlich';
    if (!formData.email.trim()) newErrors.email = 'E-Mail ist erforderlich';
    else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = 'Ungültige E-Mail-Adresse';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    try {
      if (student) {
        await studentService.update(student.id, formData);
      } else {
        await studentService.create(formData);
      }
      onSave();
    } catch (error) {
      console.error('Error saving student:', error);
      setErrors({ submit: error.message });
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {student ? 'Studierenden bearbeiten' : 'Neuen Studierenden hinzufügen'}
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Studierenden-ID"
              name="student_id"
              value={formData.student_id}
              onChange={handleChange}
              error={!!errors.student_id}
              helperText={errors.student_id}
              required
            />
          </Grid>
          <Grid item xs={6}>
            <Select
              name="program"
              label="Studiengang"
              fullWidth
              value={formData.program}
              onChange={handleChange}
              options={[
                { value: 'GS', label: 'Grundschule' },
                { value: 'MS', label: 'Mittelschule' }
              ]}
              showAllOption={false}
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Vorname"
              name="first_name"
              value={formData.first_name}
              onChange={handleChange}
              error={!!errors.first_name}
              helperText={errors.first_name}
              required
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Nachname"
              name="last_name"
              value={formData.last_name}
              onChange={handleChange}
              error={!!errors.last_name}
              helperText={errors.last_name}
              required
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="E-Mail"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              error={!!errors.email}
              helperText={errors.email}
              required
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Telefon"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Heimatadresse"
              name="home_address"
              value={formData.home_address}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Semesteradresse"
              name="semester_address"
              value={formData.semester_address}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Region"
              name="home_region"
              value={formData.home_region}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={6}>
            <Select
              name="placement_status"
              label="Platzierungsstatus"
              fullWidth
              value={formData.placement_status}
              onChange={handleChange}
              options={[
                { value: 'UNPLACED', label: 'Nicht zugewiesen' },
                { value: 'PLACED', label: 'Zugewiesen' }
              ]}
              showAllOption={false}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Notizen"
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              multiline
              rows={3}
            />
          </Grid>
        </Grid>
        {errors.submit && (
          <Typography color="error" sx={{ mt: 2 }}>
            {errors.submit}
          </Typography>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} variant="secondary">Abbrechen</Button>
        <Button onClick={handleSubmit} variant="primary">
          {student ? 'Aktualisieren' : 'Erstellen'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default StudentFormDialog;
