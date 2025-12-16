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
} from '@mui/material';
import Button from '../ui/Button';
import TextField from '../ui/TextField';
import Select from '../ui/Select';
import { createTeacher, updateTeacher } from './TeachersApi';

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
    });

    const [errors, setErrors] = useState({});
    const [saving, setSaving] = useState(false);

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
            });
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
            });
        }
        setErrors({});
    }, [teacher, open]);

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
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async () => {
        if (!validateForm()) return;

        setSaving(true);
        try {
            const dataToSend = {
                ...formData,
                anrechnungsstunden: parseFloat(formData.anrechnungsstunden) || 0,
            };

            if (teacher) {
                await updateTeacher(teacher.id, dataToSend);
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
                    <Grid item xs={12} sm={6}>
                        <TextField
                            name="preferred_praktika_raw"
                            label="Bevorzugte Praktika"
                            fullWidth
                            value={formData.preferred_praktika_raw}
                            onChange={handleChange}
                            placeholder="z.B. PDP I, SFP"
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