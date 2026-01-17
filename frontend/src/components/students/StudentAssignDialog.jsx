import React, { useState, useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  CircularProgress,
  Typography,
} from '@mui/material';
import Button from '../ui/Button';
import TextField from '../ui/TextField';
import Select from '../ui/Select';
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
      const [mentorsResponse, schoolsResponse, subjectsResponse] = await Promise.all([
        plService.getAll(),
        schoolService.getAll(),
        fetch('/api/subjects/').then(res => res.json()),
      ]);
      
      // Handle response format - might be data.data or just data
      setMentors(mentorsResponse.data || mentorsResponse);
      setSchools(schoolsResponse.data || schoolsResponse);
      
      // Filter subjects based on student's subjects
      if (student && subjectsResponse) {
        const studentSubjectIds = [
          student.primary_subject,
          student.didactic_subject_1,
          student.didactic_subject_2,
          student.didactic_subject_3,
        ].filter(Boolean);
        
        const filteredSubjects = subjectsResponse.filter(subject => 
          studentSubjectIds.includes(subject.id)
        );
        setSubjects(filteredSubjects);
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
              <Select
                name="practicum_type"
                label="Praktikumstyp *"
                fullWidth
                value={formData.practicum_type}
                onChange={handleChange}
                options={PRACTICUM_TYPES}
                showAllOption={false}
                error={!!errors.practicum_type}
                helperText={errors.practicum_type}
              />
            </Grid>
            <Grid item xs={12}>
              <Select
                name="mentor_id"
                label="Mentor *"
                fullWidth
                value={formData.mentor_id}
                onChange={handleChange}
                options={mentors.map(m => ({
                  value: m.id,
                  label: `${m.first_name} ${m.last_name} - ${m.school_name || 'Keine Schule'}`
                }))}
                showAllOption={false}
                error={!!errors.mentor_id}
                helperText={errors.mentor_id}
              />
            </Grid>
            <Grid item xs={12}>
              <Select
                name="school_id"
                label="Schule *"
                fullWidth
                value={formData.school_id}
                onChange={handleChange}
                options={schools.map(s => ({
                  value: s.id,
                  label: `${s.name} - ${s.school_type}`
                }))}
                showAllOption={false}
                error={!!errors.school_id}
                helperText={errors.school_id}
              />
            </Grid>
            <Grid item xs={12}>
              <Select
                name="subject_id"
                label="Fach *"
                fullWidth
                value={formData.subject_id}
                onChange={handleChange}
                options={subjects.map(s => ({
                  value: s.id,
                  label: s.name
                }))}
                showAllOption={false}
                error={!!errors.subject_id}
                helperText={errors.subject_id}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                name="academic_year"
                label="Akademisches Jahr"
                fullWidth
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
        <Button onClick={onClose} variant="secondary">
          Abbrechen
        </Button>
        <Button onClick={handleSubmit} variant="primary" disabled={loading}>
          Zuweisen
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default StudentAssignDialog;
