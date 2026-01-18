import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Grid,
    FormControlLabel,
    Checkbox,
    Alert
} from '@mui/material';
import Button from '../ui/Button';
import TextField from '../ui/TextField';
import Select from '../ui/Select';
import { createSchool, updateSchool } from './SchoolsApi';

const SCHOOL_TYPES = [
    { value: 'GS', label: 'Grundschule' },
    { value: 'MS', label: 'Mittelschule' },
];

/**
 * School Form Dialog for creating and editing schools
 */
const SchoolFormDialog = ({ open, onClose, onSave, school, title }) => {
    const [formData, setFormData] = useState({
        name: '',
        school_type: 'GS',
        city: '',
        district: '',
        zone: 1,
        opnv_code: '',
        distance_km: 0,
        is_active: true,
        notes: '',
        latitude: null,
        longitude: null,
    });

    const [errors, setErrors] = useState({});
    const [saving, setSaving] = useState(false);
    const [submitError, setSubmitError] = useState(null);

    // Initialize form data when school prop changes
    useEffect(() => {
        if (school) {
            setFormData({
                name: school.name || '',
                school_type: school.school_type || 'GS',
                city: school.city || '',
                district: school.district || '',
                zone: school.zone || 1,
                opnv_code: school.opnv_code || '',
                distance_km: school.distance_km || 0,
                is_active: school.is_active !== undefined ? school.is_active : true,
                notes: school.notes || '',
                latitude: school.latitude || null,
                longitude: school.longitude || null,
            });
        } else {
            // Reset form for new school
            setFormData({
                name: '',
                school_type: 'GS',
                city: '',
                district: '',
                zone: 1,
                opnv_code: '',
                distance_km: 0,
                is_active: true,
                notes: '',
                latitude: null,
                longitude: null,
            });
        }
        setErrors({});
        setSubmitError(null);
    }, [school, open]);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
        // Clear error for this field
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    const validateForm = () => {
        const newErrors = {};

        if (!formData.name.trim()) {
            newErrors.name = 'Schulname ist erforderlich';
        }
        if (!formData.city.trim()) {
            newErrors.city = 'Stadt ist erforderlich';
        }
        if (!formData.district.trim()) {
            newErrors.district = 'Bezirk ist erforderlich';
        }
        if (!formData.zone || formData.zone < 1) {
            newErrors.zone = 'Zone muss mindestens 1 sein';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async () => {
        if (!validateForm()) {
            return;
        }

        setSaving(true);
        setSubmitError(null);
        
        try {
            // Prepare data for API
            const dataToSend = {
                ...formData,
                zone: parseInt(formData.zone, 10),
                distance_km: parseFloat(formData.distance_km) || 0,
                latitude: formData.latitude ? parseFloat(formData.latitude) : null,
                longitude: formData.longitude ? parseFloat(formData.longitude) : null,
            };

            if (school) {
                // Update existing school
                await updateSchool(school.id, dataToSend);
            } else {
                // Create new school
                await createSchool(dataToSend);
            }

            onSave(); // Close and refresh parent
        } catch (error) {
            console.error('Save error:', error);
            setSubmitError(error.message || "Fehler beim Speichern der Schule.");
        } finally {
            setSaving(false);
        }
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>{title || (school ? "Schule bearbeiten" : "Neue Schule anlegen")}</DialogTitle>
            <DialogContent dividers>
                {submitError && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {submitError}
                    </Alert>
                )}

                <Grid container spacing={2} sx={{ mt: 0 }}>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            name="name"
                            label="Schulname *"
                            fullWidth
                            value={formData.name}
                            onChange={handleChange}
                            error={!!errors.name}
                            helperText={errors.name}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <Select
                            name="school_type"
                            label="Schultyp *"
                            fullWidth
                            value={formData.school_type}
                            onChange={handleChange}
                            options={SCHOOL_TYPES}
                            showAllOption={false}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            name="city"
                            label="Stadt *"
                            fullWidth
                            value={formData.city}
                            onChange={handleChange}
                            error={!!errors.city}
                            helperText={errors.city}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            name="district"
                            label="Bezirk *"
                            fullWidth
                            value={formData.district}
                            onChange={handleChange}
                            error={!!errors.district}
                            helperText={errors.district}
                        />
                    </Grid>
                    <Grid item xs={12} sm={4}>
                        <TextField
                            name="zone"
                            label="Zone *"
                            fullWidth
                            type="number"
                            value={formData.zone}
                            onChange={handleChange}
                            error={!!errors.zone}
                            helperText={errors.zone}
                            inputProps={{ min: 1 }}
                        />
                    </Grid>
                    <Grid item xs={12} sm={4}>
                        <TextField
                            name="opnv_code"
                            label="ÖPNV Code"
                            fullWidth
                            value={formData.opnv_code}
                            onChange={handleChange}
                        />
                    </Grid>
                    <Grid item xs={12} sm={4}>
                        <TextField
                            name="distance_km"
                            label="Entfernung (km)"
                            fullWidth
                            type="number"
                            value={formData.distance_km}
                            onChange={handleChange}
                            inputProps={{ step: 0.1, min: 0 }}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            name="latitude"
                            label="Breitengrad (Lat)"
                            fullWidth
                            type="number"
                            value={formData.latitude || ''}
                            onChange={handleChange}
                            inputProps={{ step: "any" }}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            name="longitude"
                            label="Längengrad (Lng)"
                            fullWidth
                            type="number"
                            value={formData.longitude || ''}
                            onChange={handleChange}
                            inputProps={{ step: "any" }}
                        />
                    </Grid>
                    <Grid item xs={12}>
                        <TextField
                            name="notes"
                            label="Notizen"
                            fullWidth
                            multiline
                            rows={3}
                            value={formData.notes}
                            onChange={handleChange}
                        />
                    </Grid>
                    <Grid item xs={12}>
                        <FormControlLabel
                            control={
                                <Checkbox
                                    name="is_active"
                                    checked={formData.is_active}
                                    onChange={handleChange}
                                    color="primary"
                                />
                            }
                            label="Schule ist aktiv (für Zuteilung verfügbar)"
                        />
                    </Grid>
                </Grid>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} variant="outlined" color="inherit">
                    Abbrechen
                </Button>
                {/* Fixed: Use variant="contained" to ensure it's visible */}
                <Button onClick={handleSubmit} variant="contained" color="primary" disabled={saving}>
                    {saving ? 'Speichern...' : 'Speichern'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default SchoolFormDialog;