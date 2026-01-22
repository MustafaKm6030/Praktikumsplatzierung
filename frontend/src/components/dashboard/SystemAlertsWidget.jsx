import React from 'react';
import { Box, Typography, Alert } from '@mui/material';
import { CheckCircle as SuccessIcon, Warning as WarningIcon, Error as ErrorIcon } from '@mui/icons-material';
import WidgetContainer from './WidgetContainer';

/**
 * Widget 3: System Alerts
 * Shows actionable alerts only
 */
const SystemAlertsWidget = ({ studentSummary = {}, budgetSummary = {}, entityCounts = {} }) => {
    const alerts = [];

    // Check for unassigned students
    const unassignedStudents = studentSummary.unassigned_students || 0;
    const totalStudents = studentSummary.total_students || 0;
    
    if (unassignedStudents > 0) {
        alerts.push({
            severity: 'error',
            icon: <ErrorIcon />,
            message: `${unassignedStudents} nicht zugewiesene Studierende benötigen Aufmerksamkeit`,
        });
    } else if (unassignedStudents === 0 && totalStudents > 0) {
        alerts.push({
            severity: 'success',
            icon: <SuccessIcon />,
            message: 'Alle Studierenden erfolgreich zugewiesen',
        });
    }

    // Check for budget issues
    const remainingBudget = budgetSummary.remaining_budget || 0;
    if (remainingBudget < 0) {
        alerts.push({
            severity: 'error',
            icon: <ErrorIcon />,
            message: `Budget um ${Math.abs(remainingBudget)} Stunden überschritten`,
        });
    } else if (remainingBudget < 10 && remainingBudget > 0) {
        alerts.push({
            severity: 'warning',
            icon: <WarningIcon />,
            message: `Niedriges Restbudget: ${remainingBudget} Stunden`,
        });
    }

    // Check overall allocation success
    if (unassignedStudents === 0 && remainingBudget >= 0 && totalStudents > 0) {
        alerts.push({
            severity: 'success',
            icon: <SuccessIcon />,
            message: 'Zuteilung erfolgreich - System bereit',
        });
    }

    return (
        <WidgetContainer
            title="Systembenachrichtigungen"
            sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
            }}
        >
            {alerts.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4, color: '#6b7280', flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Typography variant="body2">Keine Benachrichtigungen - Warte auf Zuteilungsdaten</Typography>
                </Box>
            ) : (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, flex: 1 }}>
                    {alerts.map((alert, index) => (
                        <Alert
                            key={index}
                            severity={alert.severity}
                            icon={alert.icon}
                            sx={{
                                borderRadius: '12px',
                                '& .MuiAlert-icon': {
                                    fontSize: '24px',
                                },
                            }}
                        >
                            {alert.message}
                        </Alert>
                    ))}
                </Box>
            )}
        </WidgetContainer>
    );
};

export default SystemAlertsWidget;