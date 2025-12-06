import React, { useState } from 'react';
import { Box, Typography, Paper, LinearProgress, Grid, Alert } from '@mui/material';
import { PlayArrow, CheckCircle, Warning, LocationOn } from '@mui/icons-material';
import Button from '../ui/Button';
import KPICard from '../dashboard/KPICard';
//import allocationService from '../../api/allocationService';

const AllocationRunStep = ({ onComplete }) => {
    const [status, setStatus] = useState('idle'); // 'idle' | 'running' | 'complete' | 'error'
    const [progress, setProgress] = useState(0);
    const [logs, setLogs] = useState([]);
    const [results, setResults] = useState(null);

    // Simulation of the algorithm steps (visual feedback)
    const runSimulation = () => {
        const steps = [
            "Loading 150 Student Records...",
            "Identifying Capacity Conflicts...",
            "Optimizing Travel Times (Zone 1)...",
            "Optimizing Travel Times (Zone 2)...",
            "Finalizing Matches..."
        ];

        let currentStep = 0;
        
        const interval = setInterval(() => {
            if (currentStep >= steps.length) {
                clearInterval(interval);
                finishAllocation();
                return;
            }
            
            setLogs(prev => [...prev, steps[currentStep]]);
            setProgress(prev => prev + 20);
            currentStep++;
        }, 800);
    };

    const finishAllocation = async () => {
        // Here we would fetch the REAL summary from the backend
        // For now, we mock the response
        setResults({
            matchRate: "95%",
            unmatchedCount: 5,
            avgDistance: "4.2km"
        });
        setStatus('complete');
    };

    const handleStart = async () => {
        setStatus('running');
        setLogs([]);
        setProgress(0);

        // --- MOCK MODE: ENABLED ---
        // We comment out the real API call so the UI works without the backend
        /*
        try {
            // Trigger the real backend process
            await allocationService.runAutoAllocation({});
            
            // Start visual feedback
            runSimulation();
            
        } catch (err) {
            console.error(err);
            setStatus('error');
        }
        */

        // Trigger the simulation immediately
        runSimulation();
    };

    // --- RENDER: 1. IDLE STATE ---
    if (status === 'idle' || status === 'error') {
        return (
            <Box sx={{ maxWidth: 600, mx: 'auto', textAlign: 'center', py: 4 }}>
                <Typography variant="h5" sx={{ mb: 2, fontWeight: 700 }}>
                    Run Auto-Allocation
                </Typography>
                <Typography sx={{ mb: 4, color: '#6b7280' }}>
                    This will execute the matching algorithm based on the defined constraints. 
                    Existing draft allocations will be overwritten.
                </Typography>

                {status === 'error' && (
                    <Alert severity="error" sx={{ mb: 3 }}>Failed to start allocation.</Alert>
                )}

                <Button 
                    onClick={handleStart} 
                    size="large" 
                    startIcon={<PlayArrow />}
                    sx={{ px: 4, py: 1.5 }}
                >
                    Start Allocation Algorithm
                </Button>
            </Box>
        );
    }

    // --- RENDER: 2. RUNNING STATE ---
    if (status === 'running') {
        return (
            <Paper sx={{ p: 5, maxWidth: 700, mx: 'auto', borderRadius: '16px' }}>
                <Typography variant="h6" align="center" sx={{ mb: 3 }}>
                    Running Allocation...
                </Typography>
                
                <Box sx={{ width: '100%', mb: 4 }}>
                    <LinearProgress 
                        variant="determinate" 
                        value={progress} 
                        sx={{ height: 10, borderRadius: 5, backgroundColor: '#f1f5f9', '& .MuiLinearProgress-bar': { backgroundColor: '#3b82f6' } }} 
                    />
                    <Typography align="right" variant="caption" sx={{ mt: 1, display: 'block', color: '#6b7280' }}>
                        {progress}% Complete
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
                        ▌ Processing...
                    </div>
                </Box>
            </Paper>
        );
    }

    // --- RENDER: 3. COMPLETE STATE (Results Summary) ---
    return (
        <Box>
            <Typography variant="h5" sx={{ mb: 4, fontWeight: 700, textAlign: 'center' }}>
                Allocation Results Summary
            </Typography>

            <Grid container spacing={3} sx={{ mb: 6 }}>
                <Grid item xs={12} md={4}>
                    <KPICard 
                        label="Success Rate" 
                        value={results.matchRate} 
                        icon={<CheckCircle />} 
                        color="#10b981" 
                    />
                </Grid>
                <Grid item xs={12} md={4}>
                    <KPICard 
                        label="Unmatched" 
                        value={`${results.unmatchedCount} Students`} 
                        icon={<Warning />} 
                        color="#dc2626" 
                    />
                </Grid>
                <Grid item xs={12} md={4}>
                    <KPICard 
                        label="Average Distance" 
                        value={results.avgDistance} 
                        icon={<LocationOn />} 
                        color="#6b7280" 
                    />
                </Grid>
            </Grid>

            <Box sx={{ textAlign: 'center' }}>
                <Button 
                    onClick={onComplete} // Moves to Step 3 (Review)
                    size="large" 
                    variant="primary"
                >
                    Review Draft Allocation
                </Button>
            </Box>
        </Box>
    );
};

export default AllocationRunStep;