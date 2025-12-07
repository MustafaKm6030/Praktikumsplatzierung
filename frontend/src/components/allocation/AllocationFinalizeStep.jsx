import React from 'react';
import { Box, Typography, Paper, Grid, Divider } from '@mui/material';
import { 
    CheckCircleOutline, 
    FileDownload, 
    PictureAsPdf, 
    Send, 
    Dashboard as DashboardIcon 
} from '@mui/icons-material';
import Button from '../ui/Button';
import { useNavigate } from 'react-router-dom';

const AllocationFinalizeStep = () => {
    const navigate = useNavigate();

    const handleDownloadCsv = () => alert("Downloading CSV export...");
    const handleDownloadPdf = () => alert("Generating PDF reports...");
    const handlePublish = () => alert("Publishing results to student portal...");

    return (
        <Box sx={{ maxWidth: 800, mx: 'auto' }}>
            
            {/* Success Hero Section */}
            <Paper sx={{ p: 6, textAlign: 'center', borderRadius: '16px', mb: 4, bgcolor: '#f0fdf4', border: '1px solid #bbf7d0' }}>
                <CheckCircleOutline sx={{ fontSize: 80, color: '#16a34a', mb: 2 }} />
                <Typography variant="h4" sx={{ fontWeight: 700, color: '#166534', mb: 1 }}>
                    Allocation Cycle Complete!
                </Typography>
                <Typography variant="body1" sx={{ color: '#15803d' }}>
                    All assignments have been reviewed and are ready for publication.
                </Typography>
            </Paper>

            {/* Actions Grid */}
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600, color: '#374151' }}>
                Post-Allocation Actions
            </Typography>

            <Grid container spacing={3}>
                {/* Export Data */}
                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 3, borderRadius: '12px', height: '100%' }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                            <FileDownload fontSize="small" /> Data Exports
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 3, color: '#6b7280' }}>
                            Download the raw assignment data for external systems or Excel archival.
                        </Typography>
                        <Button onClick={handleDownloadCsv} variant="secondary" fullWidth startIcon={<FileDownload />}>
                            Export Master List (CSV)
                        </Button>
                    </Paper>
                </Grid>

                {/* Generate Reports */}
                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 3, borderRadius: '12px', height: '100%' }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                            <PictureAsPdf fontSize="small" /> Official Documents
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 3, color: '#6b7280' }}>
                            Generate assignment letters for Schools, PLs, and Students.
                        </Typography>
                        <Button onClick={handleDownloadPdf} variant="secondary" fullWidth startIcon={<PictureAsPdf />}>
                            Generate PDF Bundle
                        </Button>
                    </Paper>
                </Grid>
            </Grid>

            <Divider sx={{ my: 6 }} />

            {/* Final Actions */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Button 
                    onClick={() => navigate('/')} 
                    variant="secondary" 
                    startIcon={<DashboardIcon />}
                >
                    Return to Dashboard
                </Button>

                <Button 
                    onClick={handlePublish} 
                    size="large" 
                    startIcon={<Send />}
                    sx={{ px: 4 }}
                >
                    Publish Results
                </Button>
            </Box>
        </Box>
    );
};

export default AllocationFinalizeStep;