import React, { useState, useEffect } from 'react';
import { Box, Stepper, Step, StepLabel, Typography, Container } from '@mui/material';

import DemandOverviewStep from '../components/allocation/DemandOverviewStep';
import AllocationRunStep from '../components/allocation/AllocationRunStep';
import AllocationResultsStep from '../components/allocation/AllocationResultsStep';
import AllocationFinalizeStep from '../components/allocation/AllocationFinalizeStep';
import allocationService from '../api/allocationService';

// Workflow steps
const STEPS = [
    'Bedarfsübersicht',
    'Automatische Zuteilung durchführen',
    'Ergebnisse überprüfen',
    'Abschließen'
];

export default function Allocation() {

    const [activeStep, setActiveStep] = useState(0);

    useEffect(() => {
        const checkExistingAssignments = async () => {
            try {
                const response = await allocationService.getAssignments();
                const assignments = response.data || [];
                if (assignments.length > 0) {
                    setActiveStep(2);
                }
            } catch (err) {
                console.error('Failed to check existing assignments:', err);
            }
        };

        checkExistingAssignments();
    }, []);

    const handleStepComplete = () => {
        setActiveStep((prev) => (prev < STEPS.length - 1 ? prev + 1 : 0));
    };

    return (
        <Box sx={{ p: 3, pt: '40px', minHeight: '100vh' }}>
            <Container maxWidth="lg">
                {/* Header */}
                <Typography variant="h4" sx={{ mb: 1, fontWeight: 700, color: '#1f2937' }}>
                    Praktikumsplanung & Zuteilung
                </Typography>
                <Typography variant="body1" sx={{ mb: 5, color: '#6b7280' }}>
                    Studierende mit verfügbaren Praktikumslehrkräften und Schulplätzen zusammenführen.
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
                        <AllocationResultsStep 
                            onComplete={handleStepComplete}
                            onReset={() => setActiveStep(0)}
                        />
                    )}

                    {/* STEP 4: FINALIZE */}
                    {activeStep === 3 && (
                        <AllocationFinalizeStep />
                    )}
                </Box>
            </Container>
        </Box>
    );
}