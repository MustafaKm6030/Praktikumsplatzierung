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
 * School View Dialog for displaying school details
 */
const SchoolViewDialog = ({ open, onClose, school }) => {
    if (!school) return null;

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
                    <span>Schuldetails</span>
                    <Chip
                        label={school.is_active ? 'Aktiv' : 'Inaktiv'}
                        color={school.is_active ? 'success' : 'error'}
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

                    <InfoRow label="Schulname" value={school.name} />
                    <InfoRow
                        label="Schultyp"
                        value={school.school_type === 'GS' ? 'Grundschule' : school.school_type === 'MS' ? 'Mittelschule' : school.school_type}
                    />
                    <InfoRow label="Stadt" value={school.city} />
                    <InfoRow label="Bezirk" value={school.district} />

                    <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                        Standortinformationen
                    </Typography>
                    <Divider sx={{ mb: 2 }} />

                    <InfoRow label="Zone" value={school.zone} />
                    <InfoRow label="ÖPNV Code" value={school.opnv_code} />
                    <InfoRow label="Entfernung (km)" value={school.distance_km} />
                    {school.latitude && school.longitude && (
                        <>
                            <InfoRow label="Breitengrad" value={school.latitude} />
                            <InfoRow label="Längengrad" value={school.longitude} />
                        </>
                    )}

                    {school.notes && (
                        <>
                            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                                Notizen
                            </Typography>
                            <Divider sx={{ mb: 2 }} />
                            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                                {school.notes}
                            </Typography>
                        </>
                    )}

                    {(school.created_at || school.updated_at) && (
                        <>
                            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                                Metadaten
                            </Typography>
                            <Divider sx={{ mb: 2 }} />
                            {school.created_at && (
                                <InfoRow
                                    label="Erstellt am"
                                    value={new Date(school.created_at).toLocaleString('de-DE')}
                                />
                            )}
                            {school.updated_at && (
                                <InfoRow
                                    label="Aktualisiert am"
                                    value={new Date(school.updated_at).toLocaleString('de-DE')}
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

export default SchoolViewDialog;