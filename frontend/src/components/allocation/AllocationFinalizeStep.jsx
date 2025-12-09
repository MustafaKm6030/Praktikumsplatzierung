import React, { useState } from 'react';
import { Box, Typography, Paper, Grid, Divider } from '@mui/material';
import {
    CheckCircleOutline,
    FileDownload,
    PictureAsPdf,
    Dashboard as DashboardIcon
} from '@mui/icons-material';
import Button from '../ui/Button';
import { useNavigate } from 'react-router-dom';
import allocationService from '../../api/allocationService';

const AllocationFinalizeStep = () => {
    const navigate = useNavigate();
    const [isLoadingExcel, setIsLoadingExcel] = useState(false);
    const [isLoadingPdf, setIsLoadingPdf] = useState(false);

    const handleDownloadExcel = async () => {
        setIsLoadingExcel(true);
        try {
            const response = await allocationService.exportExcel();
            const blob = new Blob([response.data], {
                type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            });
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'praktikumszuteilungen.xlsx';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Excel export failed:', error);
            alert('Excel-Export fehlgeschlagen. Bitte versuchen Sie es erneut.');
        } finally {
            setIsLoadingExcel(false);
        }
    };

    const handleDownloadPdf = async () => {
        setIsLoadingPdf(true);
        try {
            const response = await allocationService.exportPDF();
            const blob = new Blob([response.data], { type: 'application/pdf' });
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'praktikumszuteilungen.pdf';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('PDF export failed:', error);
            alert('PDF-Export fehlgeschlagen. Bitte versuchen Sie es erneut.');
        } finally {
            setIsLoadingPdf(false);
        }
    };

    return (
        <Box sx={{ maxWidth: 800, mx: 'auto' }}>

            {/* Success Hero Section */}
            <Paper sx={{ p: 6, textAlign: 'center', borderRadius: '16px', mb: 4, bgcolor: '#f0fdf4', border: '1px solid #bbf7d0' }}>
                <CheckCircleOutline sx={{ fontSize: 80, color: '#16a34a', mb: 2 }} />
                <Typography variant="h4" sx={{ fontWeight: 700, color: '#166534', mb: 1 }}>
                    Zuteilungszyklus abgeschlossen!
                </Typography>
                <Typography variant="body1" sx={{ color: '#15803d' }}>
                    Alle Zuweisungen wurden überprüft und sind zur Veröffentlichung bereit.
                </Typography>
            </Paper>

            {/* Actions Grid */}
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600, color: '#374151' }}>
                Aktionen nach der Zuteilung
            </Typography>

            <Grid container spacing={3}>
                {/* Export Data */}
                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 3, borderRadius: '12px', height: '100%' }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                            <FileDownload fontSize="small" /> Datenexporte
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 3, color: '#6b7280' }}>
                            Laden Sie die Zuweisungsdaten für externe Systeme oder Excel-Archivierung herunter.
                        </Typography>
                        <Button
                            onClick={handleDownloadExcel}
                            variant="secondary"
                            fullWidth
                            startIcon={<FileDownload />}
                            disabled={isLoadingExcel}
                        >
                            {isLoadingExcel ? 'Wird exportiert...' : 'Masterliste exportieren (Excel)'}
                        </Button>
                    </Paper>
                </Grid>

                {/* Generate Reports */}
                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 3, borderRadius: '12px', height: '100%' }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                            <PictureAsPdf fontSize="small" /> Offizielle Dokumente
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 3, color: '#6b7280' }}>
                            Erstellen Sie Zuweisungsschreiben für Schulen, Praktikumslehrkräfte und Studierende.
                        </Typography>
                        <Button
                            onClick={handleDownloadPdf}
                            variant="secondary"
                            fullWidth
                            startIcon={<PictureAsPdf />}
                            disabled={isLoadingPdf}
                        >
                            {isLoadingPdf ? 'Wird generiert...' : 'PDF-Paket generieren'}
                        </Button>
                    </Paper>
                </Grid>
            </Grid>

            <Divider sx={{ my: 6 }} />

            {/* Final Actions */}
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <Button
                    onClick={() => navigate('/')}
                    variant="secondary"
                    startIcon={<DashboardIcon />}
                >
                    Zum Dashboard zurückkehren
                </Button>
            </Box>
        </Box>
    );
};

export default AllocationFinalizeStep;