import React, { useState } from 'react';
import { Box, Typography, Paper, LinearProgress, Grid, Alert } from '@mui/material';
import { PlayArrow, CheckCircle, Warning } from '@mui/icons-material';
import Button from '../ui/Button';
import KPICard from '../dashboard/KPICard';
import allocationService from '../../api/allocationService';

const AllocationRunStep = ({ onComplete, onAllocationRun, allocationRun }) => {
    const [status, setStatus] = useState('idle');
    const [progress, setProgress] = useState(0);
    const [logs, setLogs] = useState([]);
    const [results, setResults] = useState(null);

    const updateProgress = (step, message) => {
        setLogs(prev => [...prev, message]);
        setProgress(step * 20);
    };

    const handleStart = async () => {
        setStatus('running');
        setLogs([]);
        setProgress(0);

        try {
            updateProgress(1, "Studierendendaten werden geladen...");
            updateProgress(2, "Mentor-Kapazität wird analysiert...");
            updateProgress(3, "Bedarf wird berechnet...");
            updateProgress(4, "Optimierungsalgorithmus läuft...");

            const response = await allocationService.runAutoAllocation({});
            const solverResult = response.data;

            updateProgress(5, "Zuordnungen werden finalisiert...");

            const totalAssignments = solverResult.total_assignments || 0;
            const totalUnassigned = solverResult.total_unassigned || 0;
            const totalMentors = totalAssignments + totalUnassigned;
            const matchRate = totalMentors > 0
                ? Math.round((totalAssignments / totalMentors) * 100)
                : 0;

            setResults({
                matchRate: `${matchRate}%`,
                unmatchedCount: totalUnassigned,
                totalAssignments: totalAssignments,
                status: solverResult.status
            });
            setStatus('complete');
            setProgress(100);

            // Trigger the parent to show AllocationResultsStep
            if (onAllocationRun) {
                onAllocationRun(true);
            }

        } catch (err) {
            console.error('Allocation error:', err);
            setLogs(prev => [...prev, `Fehler: ${err.message || 'Zuteilung fehlgeschlagen'}`]);
            setStatus('error');
        }
    };

    //  1. IDLE STATE
    if (status === 'idle' || status === 'error') {
        return (
            <Box sx={{ maxWidth: 600, mx: 'auto', textAlign: 'center', py: 4 }}>
                <Typography variant="h5" sx={{ mb: 2, fontWeight: 700 }}>
                    Automatische Zuteilung durchführen
                </Typography>
                <Typography sx={{ mb: 4, color: '#6b7280' }}>
                    Dies führt den Zuordnungsalgorithmus basierend auf den definierten Einschränkungen aus.
                    Bestehende Entwurfszuteilungen werden überschrieben.
                </Typography>

                {status === 'error' && (
                    <Alert severity="error" sx={{ mb: 3 }}>Zuteilung konnte nicht gestartet werden.</Alert>
                )}

                <Button
                    onClick={handleStart}
                    size="large"
                    startIcon={<PlayArrow />}
                    sx={{ px: 4, py: 1.5 }}
                >
                    Zuteilungsalgorithmus starten
                </Button>
            </Box>
        );
    }

    // 2. RUNNING STATE
    if (status === 'running') {
        return (
            <Paper sx={{ p: 5, maxWidth: 700, mx: 'auto', borderRadius: '16px' }}>
                <Typography variant="h6" align="center" sx={{ mb: 3 }}>
                    Zuteilung läuft...
                </Typography>

                <Box sx={{ width: '100%', mb: 4 }}>
                    <LinearProgress
                        variant="determinate"
                        value={progress}
                        sx={{ height: 10, borderRadius: 5, backgroundColor: '#f1f5f9', '& .MuiLinearProgress-bar': { backgroundColor: '#3b82f6' } }}
                    />
                    <Typography align="right" variant="caption" sx={{ mt: 1, display: 'block', color: '#6b7280' }}>
                        {progress}% Abgeschlossen
                    </Typography>
                </Box>

                <Box sx={{
                    bgcolor: '#f8fafc',
                    p: 2,
                    borderRadius: '8px',
                    height: 150,
                    overflowY: 'auto',
                    border: '1px solid #e2e8f0',
                    fontFamily: 'monospace',
                    fontSize: '0.85rem'
                }}>
                    {logs.map((log, index) => (
                        <div key={index} style={{ marginBottom: '4px', color: '#475569' }}>
                            ✓ {log}
                        </div>
                    ))}
                    <div style={{ animation: 'pulse 1s infinite', color: '#3b82f6' }}>
                        ▌ Verarbeitung läuft...
                    </div>
                </Box>
            </Paper>
        );
    }

    //3. COMPLETE STATE (
    return (
        <Box>
            <Typography variant="h5" sx={{ mb: 4, fontWeight: 700, textAlign: 'center' }}>
                Zuteilungsergebnisse - Zusammenfassung
            </Typography>

            <Grid container spacing={3} sx={{ mb: 6 }}>
                <Grid item xs={12} md={4}>
                    <KPICard
                        label="Erfolgsquote"
                        value={results.matchRate}
                        icon={<CheckCircle />}
                        color="#10b981"
                    />
                </Grid>
                <Grid item xs={12} md={4}>
                    <KPICard
                        label="Gesamtzuweisungen"
                        value={results.totalAssignments || 0}
                        icon={<CheckCircle />}
                        color="#3b82f6"
                    />
                </Grid>
                <Grid item xs={12} md={4}>
                    <KPICard
                        label="Nicht zugewiesene Lehrkräfte"
                        value={results.unmatchedCount || 0}
                        icon={<Warning />}
                        color="#dc2626"
                    />
                </Grid>
            </Grid>
        </Box>
    );
};

export default AllocationRunStep;