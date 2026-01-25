import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Grid,
    FormControlLabel,
    Checkbox,
    Typography,
    Autocomplete,
    TextField as MuiTextField,
} from '@mui/material';
import Button from '../ui/Button';
import TextField from '../ui/TextField';
import Select from '../ui/Select';
import { createTeacher, patchTeacher } from './TeachersApi';
import subjectService from '../../api/subjectService';
import schoolService from '../../api/schoolService';

const PROGRAM_OPTIONS = [
    { value: 'GS', label: 'Grundschule' },
    { value: 'MS', label: 'Mittelschule' },
];

/**
 * Teacher Form Dialog for creating and editing teachers
 */
const TeacherFormDialog = ({ open, onClose, onSave, teacher, title }) => {
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        school: null,
        program: 'GS',
        schulamt: '',
        anrechnungsstunden: 0,
        preferred_praktika_raw: '',
        is_active: true,
        available_subjects: [],
    });

    const [errors, setErrors] = useState({});
    const [saving, setSaving] = useState(false);
    const [subjects, setSubjects] = useState([]);
    const [selectedSubjects, setSelectedSubjects] = useState([]);
    const [schools, setSchools] = useState([]);
    const [selectedSchool, setSelectedSchool] = useState(null);
    const [praktikumTypes, setPraktikumTypes] = useState([]);
    const [selectedPraktikumTypes, setSelectedPraktikumTypes] = useState([]);

    // Fetch subjects, schools, and praktikum types on component mount
    useEffect(() => {
        const fetchData = async () => {
            try {
                const [subjectsResponse, schoolsResponse, praktikumTypesResponse] = await Promise.all([
                    subjectService.getActive(),
                    schoolService.getAll(),
                    subjectService.getPraktikumTypes()
                ]);
                setSubjects(subjectsResponse.data || []);
                setSchools(schoolsResponse.data || []);
                setPraktikumTypes(praktikumTypesResponse.data || []);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };
        fetchData();
    }, []);

    // Initialize form data
    useEffect(() => {
        if (teacher) {
            setFormData({
                first_name: teacher.first_name || '',
                last_name: teacher.last_name || '',
                email: teacher.email || '',
                phone: teacher.phone || '',
                school: teacher.school || null,
                program: teacher.program || 'GS',
                schulamt: teacher.schulamt || '',
                anrechnungsstunden: teacher.anrechnungsstunden || 0,
                preferred_praktika_raw: teacher.preferred_praktika_raw || '',
                is_active: teacher.is_active !== undefined ? teacher.is_active : true,
                available_subjects: teacher.available_subjects || [],
                available_praktikum_types: teacher.available_praktikum_types || [],
            });
            
            // Set selected school for Autocomplete
            if (teacher.school && schools.length > 0) {
                const school = schools.find(s => s.id === teacher.school);
                setSelectedSchool(school || null);
            } else {
                setSelectedSchool(null);
            }
            
            // Set selected subjects for Autocomplete
            if (teacher.available_subjects && Array.isArray(teacher.available_subjects)) {
                const selected = subjects.filter(subj => 
                    teacher.available_subjects.includes(subj.id)
                );
                setSelectedSubjects(selected);
            } else {
                setSelectedSubjects([]);
            }
            
            // Set selected praktikum types for Autocomplete
            if (teacher.available_praktikum_types && Array.isArray(teacher.available_praktikum_types)) {
                const selected = praktikumTypes.filter(pt => 
                    teacher.available_praktikum_types.includes(pt.id)
                );
                setSelectedPraktikumTypes(selected);
            } else {
                setSelectedPraktikumTypes([]);
            }
        } else {
            setFormData({
                first_name: '',
                last_name: '',
                email: '',
                phone: '',
                school: null,
                program: 'GS',
                schulamt: '',
                anrechnungsstunden: 0,
                preferred_praktika_raw: '',
                is_active: true,
                available_subjects: [],
                available_praktikum_types: [],
            });
            setSelectedSchool(null);
            setSelectedSubjects([]);
            setSelectedPraktikumTypes([]);
        }
        setErrors({});
    }, [teacher, open, subjects, schools, praktikumTypes]);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    const validateForm = () => {
        const newErrors = {};
        if (!formData.first_name.trim()) newErrors.first_name = 'Vorname ist erforderlich';
        if (!formData.last_name.trim()) newErrors.last_name = 'Nachname ist erforderlich';
        if (!formData.email.trim()) {
            newErrors.email = 'E-Mail ist erforderlich';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Ungültige E-Mail-Adresse';
        }
        if (!formData.school) newErrors.school = 'Schule ist erforderlich';
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSchoolChange = (event, newValue) => {
        setSelectedSchool(newValue);
        setFormData(prev => ({
            ...prev,
            school: newValue ? newValue.id : null
        }));
        // Clear school error if school is selected
        if (newValue && errors.school) {
            setErrors(prev => ({ ...prev, school: '' }));
        }
    };

    const handleSubjectsChange = (event, newValue) => {
        setSelectedSubjects(newValue);
        setFormData(prev => ({
            ...prev,
            available_subjects: newValue.map(subj => subj.id)
        }));
    };

    const handlePraktikumTypesChange = (event, newValue) => {
        setSelectedPraktikumTypes(newValue);
        setFormData(prev => ({
            ...prev,
            available_praktikum_types: newValue.map(pt => pt.id)
        }));
    };

    const handleSubmit = async () => {
        if (!validateForm()) return;

        setSaving(true);
        try {
            const dataToSend = {
                first_name: formData.first_name,
                last_name: formData.last_name,
                email: formData.email,
                phone: formData.phone || '',
                school: formData.school,
                program: formData.program,
                schulamt: formData.schulamt || '',
                anrechnungsstunden: parseFloat(formData.anrechnungsstunden) || 0,
                is_active: formData.is_active,
                available_subjects: formData.available_subjects || [],
                available_praktikum_types: formData.available_praktikum_types || [],
            };

            if (teacher) {
                await patchTeacher(teacher.id, dataToSend);
            } else {
                await createTeacher(dataToSend);
            }
            onSave();
        } catch (error) {
            console.error('Save error:', error);
            setErrors({ submit: error.message });
        } finally {
            setSaving(false);
        }
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>{title}</DialogTitle>
            <DialogContent>
                <Grid container spacing={2} sx={{ mt: 1 }}>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            name="first_name"
                            label="Vorname *"
                            fullWidth
                            value={formData.first_name}
                            onChange={handleChange}
                            error={!!errors.first_name}
                            helperText={errors.first_name}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            name="last_name"
                            label="Nachname *"
                            fullWidth
                            value={formData.last_name}
                            onChange={handleChange}
                            error={!!errors.last_name}
                            helperText={errors.last_name}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            name="email"
                            label="E-Mail *"
                            fullWidth
                            type="email"
                            value={formData.email}
                            onChange={handleChange}
                            error={!!errors.email}
                            helperText={errors.email}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            name="phone"
                            label="Telefon"
                            fullWidth
                            value={formData.phone}
                            onChange={handleChange}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <Autocomplete
                            value={selectedSchool}
                            onChange={handleSchoolChange}
                            options={schools}
                            getOptionLabel={(option) => option.name || ''}
                            renderInput={(params) => (
                                <MuiTextField
                                    {...params}
                                    label="Schule *"
                                    placeholder="Schule auswählen..."
                                    error={!!errors.school}
                                    helperText={errors.school}
                                />
                            )}
                            isOptionEqualToValue={(option, value) => option.id === value.id}
                            fullWidth
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <Select
                            name="program"
                            label="Studiengang *"
                            fullWidth
                            value={formData.program}
                            onChange={handleChange}
                            options={PROGRAM_OPTIONS}
                            showAllOption={false}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            name="schulamt"
                            label="Schulamt"
                            fullWidth
                            value={formData.schulamt}
                            onChange={handleChange}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            name="anrechnungsstunden"
                            label="Anrechnungsstunden"
                            fullWidth
                            type="number"
                            value={formData.anrechnungsstunden}
                            onChange={handleChange}
                            step="0.5"
                        />
                    </Grid>
                    <Grid item xs={12}>
                        <Autocomplete
                            multiple
                            options={praktikumTypes}
                            getOptionLabel={(option) => {
                                if (option.name) return option.name;
                                if (option.code) {
                                    const codeMap = {
                                        'PDP_I': 'PDP I (Pädagogisch-didaktisches Praktikum I)',
                                        'PDP_II': 'PDP II (Pädagogisch-didaktisches Praktikum II)',
                                        'SFP': 'SFP (Studienbegleitendes Fachpraktikum)',
                                        'ZSP': 'ZSP (Zusätzliches studienbegleitendes Praktikum)'
                                    };
                                    return codeMap[option.code] || option.code;
                                }
                                return String(option);
                            }}
                            value={selectedPraktikumTypes}
                            onChange={handlePraktikumTypesChange}
                            renderInput={(params) => (
                                <MuiTextField
                                    {...params}
                                    label="Bevorzugte Praktika"
                                    placeholder="Praktika auswählen..."
                                />
                            )}
                            isOptionEqualToValue={(option, value) => option.id === value.id}
                        />
                    </Grid>
                    <Grid item xs={12}>
                        <Autocomplete
                            multiple
                            options={subjects}
                            getOptionLabel={(option) => `${option.code} - ${option.name}`}
                            value={selectedSubjects}
                            onChange={handleSubjectsChange}
                            renderInput={(params) => (
                                <MuiTextField
                                    {...params}
                                    label="Verfügbare Fächer"
                                    placeholder="Fächer auswählen..."
                                />
                            )}
                            isOptionEqualToValue={(option, value) => option.id === value.id}
                        />
                    </Grid>
                    <Grid item xs={12}>
                        <FormControlLabel
                            control={
                                <Checkbox
                                    name="is_active"
                                    checked={formData.is_active}
                                    onChange={handleChange}
                                />
                            }
                            label="Verfügbar"
                        />
                    </Grid>
                    {errors.submit && (
                        <Grid item xs={12}>
                            <Typography color="error">{errors.submit}</Typography>
                        </Grid>
                    )}
                </Grid>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} variant="secondary">
                    Abbrechen
                </Button>
                <Button onClick={handleSubmit} variant="primary" disabled={saving}>
                    {saving ? 'Speichern...' : 'Speichern'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default TeacherFormDialog;