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
import Select from '../ui/Select';
import studentService from '../../api/studentService';

const StudentAssignDialog = ({ open, onClose, onSave, student }) => {
  const [formData, setFormData] = useState({
    practicum_type: '',
    mentor_id: '',
    school_id: '',
    subject_id: '',
  });

  const [assignmentData, setAssignmentData] = useState({
    assignments: [],
    practicum_types: [],
    subjects: [],
    schools: [],
    allSchools: [], // All schools from API, not filtered by school_type
    mentors: [],
  });

  const [filteredSubjects, setFilteredSubjects] = useState([]);
  const [filteredSchools, setFilteredSchools] = useState([]);
  const [filteredMentors, setFilteredMentors] = useState([]);
  const [selectedSchool, setSelectedSchool] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const loadAssignmentData = useCallback(async () => {
    if (!student || !student.program) return;
    
    setLoading(true);
    try {
      const response = await studentService.getAssignmentOptions();
      const data = response.data || {};
      
      const studentProgram = student.program;
      
      const filteredAssignments = (data.assignments || []).filter(
        a => a.mentor_program === studentProgram
      );
      
      const relevantPracticumTypeIds = new Set();
      const relevantSubjectIds = new Set();
      const relevantSchoolIds = new Set();
      const relevantMentorIds = new Set();
      
      filteredAssignments.forEach(assignment => {
        if (assignment.practicum_type_id) {
          relevantPracticumTypeIds.add(assignment.practicum_type_id);
        }
        if (assignment.subject_id) {
          relevantSubjectIds.add(assignment.subject_id);
        }
        if (assignment.school_id) {
          relevantSchoolIds.add(assignment.school_id);
        }
        if (assignment.mentor_id) {
          relevantMentorIds.add(assignment.mentor_id);
        }
      });
      
      const filteredPracticumTypes = (data.practicum_types || []).filter(
        pt => relevantPracticumTypeIds.has(pt.id)
      );
      
      const filteredSubjects = (data.subjects || []).filter(
        s => relevantSubjectIds.has(s.id)
      );
      
      const filteredSchools = (data.schools || []).filter(
        s => {
          if (!relevantSchoolIds.has(s.id)) return false;
          const schoolType = s.school_type;
          if (studentProgram === 'GS') {
            return schoolType === 'GS' || schoolType === 'GMS';
          } else if (studentProgram === 'MS') {
            return schoolType === 'MS' || schoolType === 'GMS';
          }
          return true;
        }
      );
      
      const filteredMentors = (data.mentors || []).filter(
        m => relevantMentorIds.has(m.id)
      );
      
      setAssignmentData({
        assignments: filteredAssignments,
        practicum_types: filteredPracticumTypes,
        subjects: filteredSubjects,
        schools: filteredSchools,
        allSchools: data.schools || [], // Store all schools for subject-based filtering
        mentors: filteredMentors,
      });
    } catch (error) {
      console.error('Error loading assignment data:', error);
    } finally {
      setLoading(false);
    }
  }, [student]);

  const isPDPType = useCallback(() => {
    if (!formData.practicum_type || !assignmentData.practicum_types || assignmentData.practicum_types.length === 0) return false;
    const practicumType = assignmentData.practicum_types.find(pt => pt.id === parseInt(formData.practicum_type));
    return practicumType && (practicumType.code === 'PDP1' || practicumType.code === 'PDP2' || practicumType.code === 'PDP_I' || practicumType.code === 'PDP_II');
  }, [formData.practicum_type, assignmentData.practicum_types]);

  useEffect(() => {
    if (open && student) {
      loadAssignmentData();
      setFormData({
        practicum_type: '',
        mentor_id: '',
        school_id: '',
        subject_id: '',
      });
      setSelectedSchool(null);
      setFilteredSubjects([]);
      setFilteredSchools([]);
      setFilteredMentors([]);
      setErrors({});
    }
  }, [open, student, loadAssignmentData]);

  useEffect(() => {
    if (!formData.practicum_type || !assignmentData.assignments || assignmentData.assignments.length === 0) {
      setFilteredSubjects([]);
      setFilteredSchools([]);
      setFilteredMentors([]);
      setSelectedSchool(null);
      return;
    }

      const practicumTypeId = parseInt(formData.practicum_type);
      const relevantAssignments = assignmentData.assignments.filter(
        a => parseInt(a.practicum_type_id) === practicumTypeId
      );
      
      const uniqueSubjectIds = new Set();
      relevantAssignments.forEach(assignment => {
        if (assignment.subject_id) {
          uniqueSubjectIds.add(parseInt(assignment.subject_id));
        }
      });
      
      const subjects = assignmentData.subjects.filter(s => 
        uniqueSubjectIds.has(parseInt(s.id))
      );
    
    setFilteredSubjects(subjects);
    setFilteredSchools([]);
    setFilteredMentors([]);
    setSelectedSchool(null);
    setFormData(prev => ({
      ...prev,
      subject_id: '',
      school_id: '',
      mentor_id: '',
    }));
  }, [formData.practicum_type, assignmentData, student]);

  useEffect(() => {
    if (!formData.practicum_type || !assignmentData.assignments || assignmentData.assignments.length === 0) {
      setFilteredSchools([]);
      setFilteredMentors([]);
      setSelectedSchool(null);
      return;
    }

    const isPDP = isPDPType();
    
    if (isPDP) {
      const practicumTypeId = parseInt(formData.practicum_type);
      const relevantAssignments = assignmentData.assignments.filter(
        a => parseInt(a.practicum_type_id) === practicumTypeId
      );
      
      const uniqueSchoolIds = new Set();
      relevantAssignments.forEach(assignment => {
        if (assignment.school_id) {
          uniqueSchoolIds.add(parseInt(assignment.school_id));
        }
      });
      
      const allAvailableSchools = assignmentData.allSchools || assignmentData.schools;
      const schools = allAvailableSchools.filter(s => 
        uniqueSchoolIds.has(parseInt(s.id))
      );
      
      setFilteredSchools(schools);
      setFilteredMentors([]);
      setSelectedSchool(null);
      setFormData(prev => ({
        ...prev,
        school_id: '',
        mentor_id: '',
      }));
    } else {
      if (!formData.subject_id) {
        setFilteredSchools([]);
        setFilteredMentors([]);
        setSelectedSchool(null);
        return;
      }

      const practicumTypeId = parseInt(formData.practicum_type);
      const subjectId = parseInt(formData.subject_id);
      
      const selectedSubject = assignmentData.subjects.find(s => 
        parseInt(s.id) === subjectId
      );
      
      if (!selectedSubject) {
        setFilteredSchools([]);
        setFilteredMentors([]);
        setSelectedSchool(null);
        return;
      }
      
      const subjectCode = selectedSubject.code;
      
      // Filter assignments by praktikum type and subject code
      const relevantAssignments = assignmentData.assignments.filter(a => {
        if (parseInt(a.practicum_type_id) !== practicumTypeId) return false;
        
        // Match by subject code if available, otherwise fall back to ID
        if (a.subject_code && a.subject_code === subjectCode) return true;
        if (a.subject_id && parseInt(a.subject_id) === subjectId) return true;
        
        return false;
      });
      
      const uniqueSchoolIds = new Set();
      relevantAssignments.forEach(assignment => {
        if (assignment.school_id) {
          uniqueSchoolIds.add(parseInt(assignment.school_id));
        }
      });
      
      const allAvailableSchools = assignmentData.allSchools || assignmentData.schools;
      const schools = allAvailableSchools.filter(s => 
        uniqueSchoolIds.has(parseInt(s.id))
      );
      
      setFilteredSchools(schools);
      setFilteredMentors([]);
      setSelectedSchool(null);
      setFormData(prev => ({
        ...prev,
        school_id: '',
        mentor_id: '',
      }));
    }
  }, [formData.practicum_type, formData.subject_id, assignmentData, student, isPDPType]);

  useEffect(() => {
    if (!formData.school_id || !assignmentData.assignments || assignmentData.assignments.length === 0) {
      setFilteredMentors([]);
      return;
    }

    const schoolId = parseInt(formData.school_id);
    const practicumTypeId = formData.practicum_type ? parseInt(formData.practicum_type) : null;
    const isPDP = isPDPType();
    
    let relevantAssignments = assignmentData.assignments.filter(
      a => parseInt(a.school_id) === schoolId
    );
    
    if (practicumTypeId) {
      relevantAssignments = relevantAssignments.filter(
        a => parseInt(a.practicum_type_id) === practicumTypeId
      );
    }
    
    if (!isPDP && formData.subject_id) {
      const subjectId = parseInt(formData.subject_id);
      const selectedSubject = assignmentData.subjects.find(s => 
        parseInt(s.id) === subjectId
      );
      
      if (selectedSubject && selectedSubject.code) {
        const subjectCode = selectedSubject.code;
        relevantAssignments = relevantAssignments.filter(a => {
          if (a.subject_code && a.subject_code === subjectCode) return true;
          if (a.subject_id && parseInt(a.subject_id) === subjectId) return true;
          return false;
        });
      }
    }
    
    const uniqueMentorIds = new Set();
    relevantAssignments.forEach(assignment => {
      if (assignment.mentor_id) {
        uniqueMentorIds.add(parseInt(assignment.mentor_id));
      }
    });
    
    const mentors = assignmentData.mentors.filter(m => 
      uniqueMentorIds.has(parseInt(m.id))
    );
    
    setFilteredMentors(mentors);
  }, [formData.school_id, formData.practicum_type, formData.subject_id, assignmentData, isPDPType]);

  const handlePracticumTypeChange = (e) => {
    const { value } = e.target;
    setFormData(prev => ({
      ...prev,
      practicum_type: value,
      subject_id: '',
      school_id: '',
      mentor_id: '',
    }));
    setSelectedSchool(null);
    if (errors.practicum_type) {
      setErrors(prev => ({ ...prev, practicum_type: null }));
    }
  };

  const handleSubjectChange = (e) => {
    const { value } = e.target;
    setFormData(prev => ({
      ...prev,
      subject_id: value,
      school_id: '',
      mentor_id: '',
    }));
    setSelectedSchool(null);
    if (errors.subject_id) {
      setErrors(prev => ({ ...prev, subject_id: null }));
    }
  };

  const handleSchoolChange = (event, newValue) => {
    setSelectedSchool(newValue);
    
    if (newValue) {
      setFormData(prev => ({
        ...prev,
        school_id: newValue.id,
        mentor_id: '',
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        school_id: '',
        mentor_id: '',
      }));
    }

    if (errors.school_id) {
      setErrors(prev => ({ ...prev, school_id: null }));
    }
  };

  const handleMentorChange = (e) => {
    const { value } = e.target;
    setFormData(prev => ({
      ...prev,
      mentor_id: value
    }));
    if (errors.mentor_id) {
      setErrors(prev => ({ ...prev, mentor_id: null }));
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.practicum_type) newErrors.practicum_type = 'Praktikumstyp ist erforderlich';
    if (!isPDPType() && !formData.subject_id) newErrors.subject_id = 'Fach ist erforderlich';
    if (!formData.school_id) newErrors.school_id = 'Schule ist erforderlich';
    if (!formData.mentor_id) newErrors.mentor_id = 'Mentor ist erforderlich';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    try {
      const practicumType = assignmentData.practicum_types.find(pt => pt.id === parseInt(formData.practicum_type));
      await studentService.assignStudent(student.id, {
        practicum_type: practicumType?.code || formData.practicum_type,
        mentor: formData.mentor_id,
        school: formData.school_id,
        subject: formData.subject_id || null,
      });
      onSave();
    } catch (error) {
      console.error('Error assigning student:', error);
      setErrors({ submit: error.response?.data?.error || error.message });
    }
  };

  const practicumTypeOptions = assignmentData.practicum_types.map(pt => ({
    value: pt.id.toString(),
    label: pt.name || pt.code
  }));

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
                onChange={handlePracticumTypeChange}
                options={practicumTypeOptions}
                showAllOption={false}
                error={!!errors.practicum_type}
                helperText={errors.practicum_type}
              />
            </Grid>
            <Grid item xs={12}>
              <Select
                name="subject_id"
                label={isPDPType() ? "Fach" : "Fach *"}
                fullWidth
                value={formData.subject_id}
                onChange={handleSubjectChange}
                options={filteredSubjects.map(s => ({
                  value: s.id.toString(),
                  label: s.display_name || s.name || s.code
                }))}
                showAllOption={false}
                error={!!errors.subject_id}
                helperText={errors.subject_id || (!formData.practicum_type ? 'Bitte wählen Sie zuerst den Praktikumstyp' : isPDPType() ? 'Für PDP1/PDP2 ist kein Fach erforderlich' : filteredSubjects.length === 0 ? 'Keine Fächer verfügbar für diesen Praktikumstyp' : '')}
                disabled={!formData.practicum_type || isPDPType()}
              />
            </Grid>
            <Grid item xs={12}>
              <Autocomplete
                options={filteredSchools}
                getOptionLabel={(option) => `${option.name} - ${option.school_type}`}
                value={selectedSchool}
                onChange={handleSchoolChange}
                disabled={!formData.practicum_type || (!isPDPType() && !formData.subject_id)}
                renderInput={(params) => (
                  <MuiTextField
                    {...params}
                    label="Schule *"
                    error={!!errors.school_id}
                    helperText={errors.school_id || (!formData.practicum_type ? 'Bitte wählen Sie zuerst den Praktikumstyp' : (!isPDPType() && !formData.subject_id) ? 'Bitte wählen Sie zuerst Praktikumstyp und Fach' : filteredSchools.length === 0 ? 'Keine Schulen verfügbar für diese Kombination' : '')}
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
                onChange={handleMentorChange}
                options={filteredMentors.map(m => ({
                  value: m.id.toString(),
                  label: `${m.first_name} ${m.last_name}`
                }))}
                showAllOption={false}
                error={!!errors.mentor_id}
                helperText={errors.mentor_id || (!formData.school_id ? 'Bitte wählen Sie zuerst die Schule' : filteredMentors.length === 0 ? 'Keine Mentoren für diese Schule verfügbar' : '')}
                disabled={!formData.school_id}
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
