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

/**
 * Teacher View Dialog for displaying teacher details
 */
const TeacherViewDialog = ({ open, onClose, teacher }) => {
    if (!teacher) return null;

    const InfoRow = ({ label, value }) => (
        <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={4}>
                <Typography variant="body2" fontWeight="bold" color="text.secondary">
                    {label}:
                </Typography>
            </Grid>
            <Grid item xs={8}>
                <Typography variant="body2">
                    {value || 'N/A'}
                </Typography>
            </Grid>
        </Grid>
    );

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>Praktikumslehrkraft Details</span>
                    <Chip
                        label={teacher.is_active ? 'Verfügbar' : 'Nicht verfügbar'}
                        color={teacher.is_active ? 'success' : 'error'}
                        size="small"
                    />
                </Box>
            </DialogTitle>
            <DialogContent>
                <Box sx={{ mt: 2 }}>
                    <Typography variant="h6" gutterBottom>
                        Grundinformationen
                    </Typography>
                    <Divider sx={{ mb: 2 }} />

                    <InfoRow label="PL-ID" value={`PL-${String(teacher.id).padStart(3, '0')}`} />
                    <InfoRow label="Name" value={`${teacher.first_name} ${teacher.last_name}`} />
                    <InfoRow label="E-Mail" value={teacher.email} />
                    <InfoRow label="Telefon" value={teacher.phone} />
                    <InfoRow label="Schule" value={teacher.school_name} />

                    <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                        Lehrdetails
                    </Typography>
                    <Divider sx={{ mb: 2 }} />

                    <InfoRow
                        label="Studiengang"
                        value={teacher.program_display || teacher.program}
                    />
                    <InfoRow label="Hauptfach" value={teacher.main_subject_name} />
                    <InfoRow label="Bevorzugte Praktika" value={teacher.preferred_praktika_raw} />
                    <InfoRow label="Schulamt" value={teacher.schulamt} />
                    <InfoRow label="Anrechnungsstunden" value={teacher.anrechnungsstunden} />
                    <InfoRow label="Kapazität" value={teacher.capacity} />

                    {(teacher.current_year_notes || teacher.notes) && (
                        <>
                            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                                Notizen
                            </Typography>
                            <Divider sx={{ mb: 2 }} />
                            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                                {teacher.current_year_notes || teacher.notes}
                            </Typography>
                        </>
                    )}

                    {(teacher.created_at || teacher.updated_at) && (
                        <>
                            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                                Metadaten
                            </Typography>
                            <Divider sx={{ mb: 2 }} />
                            {teacher.created_at && (
                                <InfoRow
                                    label="Erstellt am"
                                    value={new Date(teacher.created_at).toLocaleString('de-DE')}
                                />
                            )}
                            {teacher.updated_at && (
                                <InfoRow
                                    label="Aktualisiert am"
                                    value={new Date(teacher.updated_at).toLocaleString('de-DE')}
                                />
                            )}
                        </>
                    )}
                </Box>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} variant="primary">
                    Schließen
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default TeacherViewDialog;