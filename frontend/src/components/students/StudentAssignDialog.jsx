import React, { useState, useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  MenuItem,
  CircularProgress,
  Typography,
} from '@mui/material';
import plService from '../../api/plService';
import schoolService from '../../api/schoolService';
import studentService from '../../api/studentService';

const PRACTICUM_TYPES = [
  { value: 'PDP1', label: 'Pädagogisch-didaktisches Praktikum I' },
  { value: 'PDP2', label: 'Pädagogisch-didaktisches Praktikum II' },
  { value: 'SFP', label: 'Studienbegleitendes fachdidaktisches Praktikum' },
  { value: 'ZSP', label: 'Zusätzliches studienbegleitendes Praktikum' },
];

const StudentAssignDialog = ({ open, onClose, onSave, student }) => {
  const [formData, setFormData] = useState({
    practicum_type: '',
    mentor_id: '',
    school_id: '',
    subject_id: '',
    academic_year: new Date().getFullYear(),
  });

  const [mentors, setMentors] = useState([]);
  const [schools, setSchools] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [mentorsResponse, schoolsResponse] = await Promise.all([
        plService.getAll(),
        schoolService.getAll(),
      ]);
      setMentors(mentorsResponse.data);
      setSchools(schoolsResponse.data);

      // Get student subjects
      if (student) {
        const studentSubjects = [];
        if (student.primary_subject) studentSubjects.push({ id: student.primary_subject, name: student.primary_subject_name });
        if (student.didactic_subject_1) studentSubjects.push({ id: student.didactic_subject_1, name: student.didactic_subject_1_name });
        if (student.didactic_subject_2) studentSubjects.push({ id: student.didactic_subject_2, name: student.didactic_subject_2_name });
        if (student.didactic_subject_3) studentSubjects.push({ id: student.didactic_subject_3, name: student.didactic_subject_3_name });
        setSubjects(studentSubjects);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  }, [student]);

  useEffect(() => {
    if (open && student) {
      loadData();
    }
  }, [open, student, loadData]);

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
    if (!formData.practicum_type) newErrors.practicum_type = 'Praktikumstyp ist erforderlich';
    if (!formData.mentor_id) newErrors.mentor_id = 'Mentor ist erforderlich';
    if (!formData.school_id) newErrors.school_id = 'Schule ist erforderlich';
    if (!formData.subject_id) newErrors.subject_id = 'Fach ist erforderlich';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    try {
      await studentService.assignStudent(student.id, {
        practicum_type: formData.practicum_type,
        mentor: formData.mentor_id,
        school: formData.school_id,
        subject: formData.subject_id,
        academic_year: formData.academic_year,
      });
      onSave();
    } catch (error) {
      console.error('Error assigning student:', error);
      setErrors({ submit: error.response?.data?.error || error.message });
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        Student zuweisen: {student?.first_name} {student?.last_name}
      </DialogTitle>
      <DialogContent>
        {loading ? (
          <Grid container justifyContent="center" sx={{ py: 4 }}>
            <CircularProgress />
          </Grid>
        ) : (
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Praktikumstyp"
                name="practicum_type"
                select
                value={formData.practicum_type}
                onChange={handleChange}
                error={!!errors.practicum_type}
                helperText={errors.practicum_type}
                required
              >
                {PRACTICUM_TYPES.map(type => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Mentor"
                name="mentor_id"
                select
                value={formData.mentor_id}
                onChange={handleChange}
                error={!!errors.mentor_id}
                helperText={errors.mentor_id}
                required
              >
                {mentors.map(mentor => (
                  <MenuItem key={mentor.id} value={mentor.id}>
                    {mentor.first_name} {mentor.last_name} - {mentor.school_name}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Schule"
                name="school_id"
                select
                value={formData.school_id}
                onChange={handleChange}
                error={!!errors.school_id}
                helperText={errors.school_id}
                required
              >
                {schools.map(school => (
                  <MenuItem key={school.id} value={school.id}>
                    {school.name} - {school.school_type}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Fach"
                name="subject_id"
                select
                value={formData.subject_id}
                onChange={handleChange}
                error={!!errors.subject_id}
                helperText={errors.subject_id}
                required
              >
                {subjects.map(subject => (
                  <MenuItem key={subject.id} value={subject.id}>
                    {subject.name}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Akademisches Jahr"
                name="academic_year"
                type="number"
                value={formData.academic_year}
                onChange={handleChange}
              />
            </Grid>
          </Grid>
        )}
        {errors.submit && (
          <Typography color="error" sx={{ mt: 2 }}>
            {errors.submit}
          </Typography>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Abbrechen</Button>
        <Button onClick={handleSubmit} variant="contained" color="primary" disabled={loading}>
          Zuweisen
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default StudentAssignDialog;
