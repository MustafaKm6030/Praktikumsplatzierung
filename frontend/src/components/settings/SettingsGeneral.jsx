import React, { useState, useEffect, useCallback } from 'react';
import { Paper, Box, Typography, Grid, Stack, Snackbar, Alert, Autocomplete, TextField as MuiTextField } from '@mui/material';
import { Save as SaveIcon } from '@mui/icons-material';
import settingsService from '../../api/settingsService';
import subjectService from '../../api/subjectService';
import { getErrorMessage } from '../../api/config';
import TextField from '../ui/TextField';
import Button from '../ui/Button';
import Loader from '../ui/Loader';

// --- Internal Helper Component for DRY Sections ---
const SettingsSection = ({ title, children }) => (
    <Paper sx={{
        p: 3,
        borderRadius: '16px',
        backgroundColor: 'white',
        boxShadow: '0 2px 10px rgba(0, 0, 0, 0.08)',
        border: '1px solid rgba(248, 151, 28, 0.15)'
    }}>
        <Typography variant="h6" sx={{ fontWeight: 600, color: '#374151', mb: 3 }}>
            {title}
        </Typography>
        {children}
    </Paper>
);

function SettingsGeneral() {
    // 1. State Definitions
    const [settings, setSettings] = useState({
        id: null,
        academicYear: '',
        pdpDefaultDeadline: '',
        sfpZspDefaultDeadline: '',
        universityName: '',
        universityAddress: '',
        contactEmail: '',
        contactPhone: '',
        totalBudget: '',
        gsPercentage: '',
        msPercentage: '',
        coreSubjects: [],
    });

    const [subjects, setSubjects] = useState([]);
    const [loadingSubjects, setLoadingSubjects] = useState(false);
    const [loading, setLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [snackbar, setSnackbar] = useState({
        open: false,
        message: '',
        severity: 'success'
    });

    // 2. Helpers (Must be defined BEFORE loadSettings)

    // FIX: Wrapped in useCallback to prevent infinite loops
    const showSnackbar = useCallback((message, severity = 'success') => {
        setSnackbar({ open: true, message, severity });
    }, []);

    const handleCloseSnackbar = () => {
        setSnackbar(prev => ({ ...prev, open: false }));
    };

    const handleChange = (field, value) => {
        setSettings(prev => ({ ...prev, [field]: value }));
    };

    const loadData = useCallback(async () => {
        setLoading(true);
        setLoadingSubjects(true);
        try {
            const [subjectsResponse, settingsResponse] = await Promise.all([
                subjectService.getFromRules(),
                settingsService.getActive()
            ]);
            
            const subjectsData = subjectsResponse.data.results || subjectsResponse.data;
            setSubjects(subjectsData);
            
            const data = settingsResponse.data;
            const coreSubjectsCodes = data.core_subjects || ['D', 'MA'];
            
            const selectedSubjects = subjectsData.filter(subject => 
                coreSubjectsCodes.includes(subject.code)
            );
            
            setSettings({
                id: data.id,
                academicYear: data.current_academic_year || '',
                pdpDefaultDeadline: data.pdp_i_demand_deadline || '',
                sfpZspDefaultDeadline: data.pl_assignment_deadline || '',
                universityName: data.university_name || '',
                universityAddress: data.university_name || '',
                contactEmail: data.contact_email || '',
                contactPhone: data.contact_phone || '',
                totalBudget: data.total_anrechnungsstunden_budget || '',
                gsPercentage: data.gs_budget_percentage || '',
                msPercentage: data.ms_budget_percentage || '',
                coreSubjects: selectedSubjects,
            });
        } catch (error) {
            console.error('Error loading data:', error);
            showSnackbar('Fehler beim Laden der Daten: ' + getErrorMessage(error), 'error');
        } finally {
            setLoading(false);
            setLoadingSubjects(false);
        }
    }, [showSnackbar]);

    useEffect(() => {
        loadData();
    }, [loadData]);

    // 5. Action Handlers
    const handleSave = async (e) => {
        e.preventDefault();
        const totalPercent = Number(settings.gsPercentage) + Number(settings.msPercentage);
        if (Math.abs(totalPercent - 100) > 0.1) {
            showSnackbar(`Warnung: Die Budget-Prozentsätze ergeben zusammen ${totalPercent}%. Sie sollten idealerweise 100% ergeben.`, 'warning');
            return;
        }
        setIsSaving(true);

        try {
            if (!settings.id) throw new Error('No active settings found.');

            const coreSubjectsCodes = settings.coreSubjects.map(subject => subject.code);

            const updateData = {
                current_academic_year: settings.academicYear,
                pdp_i_demand_deadline: settings.pdpDefaultDeadline,
                pl_assignment_deadline: settings.sfpZspDefaultDeadline,
                university_name: settings.universityName,
                contact_email: settings.contactEmail,
                contact_phone: settings.contactPhone,
                total_anrechnungsstunden_budget: settings.totalBudget,
                gs_budget_percentage: settings.gsPercentage,
                ms_budget_percentage: settings.msPercentage,
                core_subjects: coreSubjectsCodes,
            };

            await settingsService.partialUpdate(settings.id, updateData);
            showSnackbar('Einstellungen erfolgreich gespeichert!', 'success');
            await loadData();
        } catch (error) {
            console.error('Error saving settings:', error);
            showSnackbar('Fehler beim Speichern: ' + getErrorMessage(error), 'error');
        } finally {
            setIsSaving(false);
        }
    };

    if (loading) return <Loader message="Einstellungen werden geladen..." />;

    return (
        <Box>
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
                <Box>
                    <Typography variant="h5" sx={{ fontWeight: 700, color: '#1f2937' }}>
                        Allgemeine Einstellungen
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#6b7280', mt: 0.5 }}>
                        Universitätsdetails und Standardeinstellungen verwalten
                    </Typography>
                </Box>

                <Button
                    onClick={handleSave}
                    variant="primary"
                    size="medium"
                    startIcon={<SaveIcon />}
                    disabled={isSaving}
                >
                    {isSaving ? 'Wird gespeichert...' : 'Änderungen speichern'}
                </Button>
            </Box>

            <form id="settings-form" onSubmit={handleSave}>
                <Stack spacing={3}>
                    <SettingsSection title="Einstellungen zum akademischen Jahr">
                        <Grid container spacing={3}>
                            <Grid item xs={12} md={6}>
                                <TextField
                                    label="Aktuelles akademisches Jahr"
                                    value={settings.academicYear}
                                    onChange={(e) => handleChange('academicYear', e.target.value)}
                                    placeholder="2024/2025"
                                    required
                                    helperText="Format: YYYY/YYYY"
                                />
                            </Grid>
                        </Grid>
                    </SettingsSection>

                    <SettingsSection title="Praktikumsfristen">
                        <Grid container spacing={3}>
                            <Grid item xs={12} md={6}>
                                <TextField
                                    label="PDP I/II Deadline"
                                    type="date"
                                    value={settings.pdpDefaultDeadline}
                                    onChange={(e) => handleChange('pdpDefaultDeadline', e.target.value)}
                                    required
                                    InputLabelProps={{ shrink: true }}
                                />
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <TextField
                                    label="SFP/ZSP Deadline"
                                    type="date"
                                    value={settings.sfpZspDefaultDeadline}
                                    onChange={(e) => handleChange('sfpZspDefaultDeadline', e.target.value)}
                                    required
                                    InputLabelProps={{ shrink: true }}
                                />
                            </Grid>
                        </Grid>
                    </SettingsSection>

                    <SettingsSection title="Universitätsinformationen">
                        <Grid container spacing={3}>
                            <Grid item xs={12}>
                                <TextField
                                    label="Universitätsname"
                                    value={settings.universityName}
                                    onChange={(e) => handleChange('universityName', e.target.value)}
                                    placeholder="Universität Passau"
                                    required
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <TextField
                                    label="Adresse"
                                    value={settings.universityAddress}
                                    onChange={(e) => handleChange('universityAddress', e.target.value)}
                                    placeholder="Innstraße 41, 94032 Passau"
                                    multiline
                                />
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <TextField
                                    label="Kontakt-E-Mail"
                                    type="email"
                                    value={settings.contactEmail}
                                    onChange={(e) => handleChange('contactEmail', e.target.value)}
                                    placeholder="praktikum@uni-passau.de"
                                    required
                                />
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <TextField
                                    label="Kontakttelefon"
                                    type="tel"
                                    value={settings.contactPhone}
                                    onChange={(e) => handleChange('contactPhone', e.target.value)}
                                    placeholder="+49 851 509-0"
                                />
                            </Grid>
                        </Grid>
                    </SettingsSection>

                    <SettingsSection title="Budgetzuweisung">
                        <Grid container spacing={3}>
                            <Grid item xs={12}>
                                <TextField
                                    label="Gesamtes Anrechnungsstunden-Budget"
                                    type="number"
                                    value={settings.totalBudget}
                                    onChange={(e) => handleChange('totalBudget', e.target.value)}
                                    step="0.01"
                                    helperText="Gesamtbudget in Stunden für die Zuteilung verfügbar"
                                />
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <TextField
                                    label="GS Budget-Prozentsatz"
                                    type="number"
                                    value={settings.gsPercentage}
                                    onChange={(e) => handleChange('gsPercentage', e.target.value)}
                                    step="0.01"
                                    helperText="Grundschule-Prozentsatz"
                                />
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <TextField
                                    label="MS Budget-Prozentsatz"
                                    type="number"
                                    value={settings.msPercentage}
                                    onChange={(e) => handleChange('msPercentage', e.target.value)}
                                    step="0.01"
                                    helperText="Mittelschule-Prozentsatz"
                                />
                            </Grid>
                        </Grid>
                    </SettingsSection>

                    <SettingsSection title="Kernfächer">
                        <Grid container spacing={3}>
                            <Grid item xs={12}>
                                <Autocomplete
                                    multiple
                                    options={subjects}
                                    getOptionLabel={(option) => `${option.code} - ${option.name}`}
                                    value={settings.coreSubjects}
                                    onChange={(event, newValue) => {
                                        handleChange('coreSubjects', newValue);
                                    }}
                                    loading={loadingSubjects}
                                    isOptionEqualToValue={(option, value) => option.code === value.code}
                                    renderInput={(params) => (
                                        <MuiTextField
                                            {...params}
                                            label="Kernfächer"
                                            placeholder="Fächer auswählen"
                                            helperText="Wählen Sie die Fächer aus, die als Kernfächer gelten sollen"
                                            sx={{
                                                '& .MuiOutlinedInput-root': {
                                                    borderRadius: '10px',
                                                    backgroundColor: 'white',
                                                },
                                            }}
                                        />
                                    )}
                                    sx={{
                                        '& .MuiChip-root': {
                                            borderRadius: '8px',
                                        },
                                    }}
                                />
                            </Grid>
                        </Grid>
                    </SettingsSection>
                </Stack>
            </form>

            <Snackbar
                open={snackbar.open}
                autoHideDuration={6000}
                onClose={handleCloseSnackbar}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            >
                <Alert
                    onClose={handleCloseSnackbar}
                    severity={snackbar.severity}
                    sx={{ width: '100%', borderRadius: '12px' }}
                    variant="filled"
                >
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </Box>
    );
}

export default SettingsGeneral;