import React, { useState, useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  CircularProgress,
  Typography,
  Autocomplete,
  TextField as MuiTextField,
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

  const [allMentors, setAllMentors] = useState([]);
  const [allSchools, setAllSchools] = useState([]);
  const [filteredMentors, setFilteredMentors] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [selectedSchool, setSelectedSchool] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingSubjects, setLoadingSubjects] = useState(false);
  const [errors, setErrors] = useState({});

  const loadInitialData = useCallback(async () => {
    setLoading(true);
    try {
      const [mentorsResponse, schoolsResponse] = await Promise.all([
        plService.getAll(),
        schoolService.getAll(),
      ]);
      
      // Handle response format - might be data.data or just data
      const mentorsData = mentorsResponse.data || mentorsResponse;
      const schoolsData = schoolsResponse.data || schoolsResponse;
      
      setAllMentors(mentorsData);
      setAllSchools(schoolsData);
      setFilteredMentors(mentorsData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadFilteredSubjects = useCallback(async (praktikumType, schoolType) => {
    if (!praktikumType || !schoolType) {
      setSubjects([]);
      return;
    }

    setLoadingSubjects(true);
    try {
      const response = await fetch(
        `/api/subjects/filtered/?praktikum_type=${praktikumType}&school_type=${schoolType}`
      );
      const data = await response.json();
      setSubjects(data);
    } catch (error) {
      console.error('Error loading filtered subjects:', error);
      setSubjects([]);
    } finally {
      setLoadingSubjects(false);
    }
  }, []);

  useEffect(() => {
    if (open && student) {
      loadInitialData();
      // Reset form when dialog opens
      setFormData({
        practicum_type: '',
        mentor_id: '',
        school_id: '',
        subject_id: '',
        academic_year: new Date().getFullYear(),
      });
      setSelectedSchool(null);
      setSubjects([]);
      setErrors({});
    }
  }, [open, student, loadInitialData]);

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

    // Load subjects when both practicum_type and school are selected
    if (name === 'practicum_type' && selectedSchool) {
      loadFilteredSubjects(value, selectedSchool.school_type);
      // Reset subject selection
      setFormData(prev => ({ ...prev, subject_id: '' }));
    }
  };

  const handleSchoolChange = (event, newValue) => {
    setSelectedSchool(newValue);
    
    if (newValue) {
      setFormData(prev => ({
        ...prev,
        school_id: newValue.id,
        mentor_id: '', // Reset mentor when school changes
        subject_id: '', // Reset subject when school changes
      }));

      // Filter mentors by selected school
      const schoolMentors = allMentors.filter(
        mentor => mentor.school === newValue.id
      );
      setFilteredMentors(schoolMentors);

      // Load subjects if practicum_type is already selected
      if (formData.practicum_type) {
        loadFilteredSubjects(formData.practicum_type, newValue.school_type);
      }
    } else {
      setFormData(prev => ({
        ...prev,
        school_id: '',
        mentor_id: '',
        subject_id: '',
      }));
      setFilteredMentors(allMentors);
      setSubjects([]);
    }

    // Clear errors
    if (errors.school_id) {
      setErrors(prev => ({ ...prev, school_id: null }));
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
              <Autocomplete
                options={allSchools}
                getOptionLabel={(option) => `${option.name} - ${option.school_type}`}
                value={selectedSchool}
                onChange={handleSchoolChange}
                renderInput={(params) => (
                  <MuiTextField
                    {...params}
                    label="Schule *"
                    error={!!errors.school_id}
                    helperText={errors.school_id}
                  />
                )}
                isOptionEqualToValue={(option, value) => option.id === value.id}
              />
            </Grid>
            <Grid item xs={12}>
              <Select
                name="mentor_id"
                label="Mentor *"
                fullWidth
                value={formData.mentor_id}
                onChange={handleChange}
                options={filteredMentors.map(m => ({
                  value: m.id,
                  label: `${m.first_name} ${m.last_name}`
                }))}
                showAllOption={false}
                error={!!errors.mentor_id}
                helperText={errors.mentor_id || (selectedSchool && filteredMentors.length === 0 ? 'Keine Mentoren für diese Schule verfügbar' : '')}
                disabled={!selectedSchool}
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
                  label: s.display_name
                }))}
                showAllOption={false}
                error={!!errors.subject_id}
                helperText={errors.subject_id || (loadingSubjects ? 'Fächer werden geladen...' : (!formData.practicum_type || !selectedSchool ? 'Bitte wählen Sie zuerst Praktikumstyp und Schule' : subjects.length === 0 ? 'Keine Fächer verfügbar für diese Kombination' : ''))}
                disabled={!formData.practicum_type || !selectedSchool || loadingSubjects}
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
