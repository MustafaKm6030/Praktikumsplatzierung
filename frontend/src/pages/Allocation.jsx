import React, { useState } from 'react';
import { Box, Stepper, Step, StepLabel, Typography, Container } from '@mui/material';

import DemandOverviewStep from '../components/allocation/DemandOverviewStep';
import AllocationRunStep from '../components/allocation/AllocationRunStep';
import AllocationResultsStep from '../components/allocation/AllocationResultsStep';
import AllocationFinalizeStep from '../components/allocation/AllocationFinalizeStep';

// Workflow steps - Combined step 2 and 3
const STEPS = [
    'Bedarfsübersicht',
    'Zuteilung durchführen & Ergebnisse überprüfen',
    'Abschließen'
];

export default function Allocation() {

    const [activeStep, setActiveStep] = useState(0);
    const [allocationRun, setAllocationRun] = useState(false); // Shared state

    const handleStepComplete = () => {
        setActiveStep((prev) => {
            const nextStep = prev < STEPS.length - 1 ? prev + 1 : 0;
            // Reset allocation state when leaving step 1
            if (nextStep !== 1) {
                setAllocationRun(false);
            }
            return nextStep;
        });
    };

    return (
        <Box sx={{ p: 3, pt: '40px', minHeight: '100vh' }}>
            <Container maxWidth="lg">

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

                    {/* STEP 2: RUN AUTO-ALLOCATION + REVIEW RESULTS (COMBINED) */}
                    {activeStep === 1 && (
                        <Box>
                            {/* Allocation Run with button at the top */}
                            <AllocationRunStep
                                onComplete={handleStepComplete}
                                onAllocationRun={setAllocationRun}
                                allocationRun={allocationRun}
                            />

                            {/* Allocation Results Summary - only show when allocation has run */}
                            {allocationRun && (
                                <Box sx={{ mt: 4 }}>
                                    <AllocationResultsStep
                                        onComplete={handleStepComplete}
                                        shouldFetch={allocationRun}
                                    />
                                </Box>
                            )}
                        </Box>
                    )}

                    {/* STEP 3: FINALIZE */}
                    {activeStep === 2 && (
                        <AllocationFinalizeStep />
                    )}
                </Box>
            </Container>
        </Box>
    );
}