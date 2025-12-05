import React, { useState } from 'react';
import { Box, Stepper, Step, StepLabel, Typography, Container, Paper } from '@mui/material';
import { ArrowForward } from '@mui/icons-material';
import Button from '../components/ui/Button';

const STEPS = [
    'Demand Overview',
    'Run Auto-Allocation',
    'Review Results',
    'Finalize'
];

export default function Allocation() {
    const [activeStep, setActiveStep] = useState(0);

    // Temporary handler to test the stepper UI
    const handleNext = () => {
        // Loop back to start if at the end, just for demo purposes
        setActiveStep((prev) => (prev < STEPS.length - 1 ? prev + 1 : 0));
    };

    return (
        <Box sx={{ p: 3, pt: '40px', minHeight: '100vh' }}>
            <Container maxWidth="lg">
                {/* 1. Header Section */}
                <Typography variant="h4" sx={{ mb: 1, fontWeight: 700, color: '#1f2937' }}>
                    Praktika Planning & Allocation
                </Typography>
                <Typography variant="body1" sx={{ mb: 5, color: '#6b7280' }}>
                    Match student demand with available PLs and school slots.
                </Typography>

                {/* 2. Workflow Stepper */}
                <Box sx={{ mb: 6 }}>
                    <Stepper activeStep={activeStep} alternativeLabel>
                        {STEPS.map((label) => (
                            <Step key={label} sx={{ 
                                '& .MuiStepLabel-root .Mui-active': { color: '#F8971C' },
                                '& .MuiStepLabel-root .Mui-completed': { color: '#10b981' },
                            }}>
                                <StepLabel>{label}</StepLabel>
                            </Step>
                        ))}
                    </Stepper>
                </Box>

                {/* 3. Step Content Placeholders */}
                <Paper sx={{ 
                    p: 6, 
                    borderRadius: '16px', 
                    minHeight: '300px',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    textAlign: 'center',
                    backgroundColor: '#fff',
                    boxShadow: '0 4px 20px rgba(0,0,0,0.05)'
                }}>
                    <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>
                        {STEPS[activeStep]}
                    </Typography>
                    
                    <Typography sx={{ mb: 4, color: '#6b7280', maxWidth: '500px' }}>
                        {activeStep === 0 && "Visualize cumulated demand for each Praktikum type and subject."}
                        {activeStep === 1 && "Configure and execute the allocation algorithm."}
                        {activeStep === 2 && "Review assignments, resolve conflicts, and make manual adjustments."}
                        {activeStep === 3 && "Generate reports, letters, and archive the planning period."}
                    </Typography>

                    {/* Temporary Demo Button - Will be replaced by specific step components later */}
                    <Button 
                        onClick={handleNext} 
                        endIcon={<ArrowForward />}
                        variant="secondary"
                    >
                        {activeStep === STEPS.length - 1 ? "Restart Demo" : "Next Step (Demo)"}
                    </Button>
                </Paper>
            </Container>
        </Box>
    );
}