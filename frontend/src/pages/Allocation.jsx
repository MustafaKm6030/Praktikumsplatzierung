import React, { useState } from 'react';
import { Box, Stepper, Step, StepLabel, Typography, Container, Paper } from '@mui/material';
import Button from '../components/ui/Button';

import AllocationRunStep from '../components/allocation/AllocationRunStep';
import AllocationResultsStep from '../components/allocation/AllocationResultsStep';
import DemandOverviewStep from '../components/allocation/DemandOverviewStep';

// Workflow steps
const STEPS = [
    'Demand Overview',
    'Run Auto-Allocation',
    'Review Results',
    'Finalize'
];

export default function Allocation() {
    
    const [activeStep, setActiveStep] = useState(0);

    const handleStepComplete = () => {
        setActiveStep((prev) => (prev < STEPS.length - 1 ? prev + 1 : 0));
    };

    return (
        <Box sx={{ p: 3, pt: '40px', minHeight: '100vh' }}>
            <Container maxWidth="lg">
                {/* Header */}
                <Typography variant="h4" sx={{ mb: 1, fontWeight: 700, color: '#1f2937' }}>
                    Praktika Planning & Allocation
                </Typography>
                <Typography variant="body1" sx={{ mb: 5, color: '#6b7280' }}>
                    Match student demand with available PLs and school slots.
                </Typography>

                {/* Workflow Stepper */}
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

                {/* Step Content */}
                <Box>
                    {/* STEP 1: DEMAND OVERVIEW */}
                    {activeStep === 0 && (
                        <DemandOverviewStep onComplete={handleStepComplete} />
                    )}
                    
                    {/* STEP 2: RUN AUTO-ALLOCATION */}
                    {activeStep === 1 && (
                        <AllocationRunStep onComplete={handleStepComplete} />
                    )}

                    {/* STEP 3: REVIEW RESULTS */}
                    {activeStep === 2 && (
                        <AllocationResultsStep onComplete={handleStepComplete} />
                    )}

                    {/* STEP 4: FINALIZE (Placeholder) */}
                    {activeStep === 3 && (
                        <Paper sx={{ p: 6, textAlign: 'center', borderRadius: '16px' }}>
                            <Typography variant="h5" sx={{ mb: 2 }}>Step 4: Finalize</Typography>
                            <Typography sx={{ mb: 4, color: '#6b7280' }}>
                                Reporting and archiving tools.
                            </Typography>
                            <Button onClick={() => setActiveStep(0)} variant="secondary">
                                Restart Wizard
                            </Button>
                        </Paper>
                    )}
                </Box>
            </Container>
        </Box>
    );
}