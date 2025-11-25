import React from 'react';
import { Box, Typography, Alert } from '@mui/material';
import { CheckCircle as SuccessIcon, Warning as WarningIcon, Error as ErrorIcon } from '@mui/icons-material';
import WidgetContainer from './WidgetContainer';

/**
 * Widget 3: System Alerts
 * Shows actionable alerts only
 */
const SystemAlertsWidget = ({ assignmentStatus = [], budgetSummary = {}, entityCounts = {} }) => {
    const alerts = [];

    // Check for unplaced students
    const unplacedStudents = entityCounts.unplaced_students || 0;
    if (unplacedStudents > 0) {
        alerts.push({
            severity: 'error',
            icon: <ErrorIcon />,
            message: `${unplacedStudents} unplaced students require attention`,
        });
    } else if (unplacedStudents === 0 && entityCounts.total_students > 0) {
        alerts.push({
            severity: 'success',
            icon: <SuccessIcon />,
            message: 'All students successfully placed',
        });
    }

    // Check for budget issues
    const remainingBudget = budgetSummary.remaining_budget || 0;
    if (remainingBudget < 0) {
        alerts.push({
            severity: 'error',
            icon: <ErrorIcon />,
            message: `Budget exceeded by ${Math.abs(remainingBudget)} hours`,
        });
    } else if (remainingBudget < 10 && remainingBudget > 0) {
        alerts.push({
            severity: 'warning',
            icon: <WarningIcon />,
            message: `Low budget remaining: ${remainingBudget} hours`,
        });
    }

    // Check for unassigned slots
    const totalUnassigned = assignmentStatus.reduce((sum, item) => sum + (item.unassigned_slots || 0), 0);
    if (totalUnassigned === 0 && assignmentStatus.length > 0) {
        alerts.push({
            severity: 'success',
            icon: <SuccessIcon />,
            message: 'All Praktika fully assigned',
        });
    } else if (totalUnassigned > 0) {
        alerts.push({
            severity: 'warning',
            icon: <WarningIcon />,
            message: `${totalUnassigned} slots unassigned across Praktika types`,
        });
    }

    // Check overall allocation success
    if (unplacedStudents === 0 && totalUnassigned === 0 && remainingBudget >= 0 && assignmentStatus.length > 0) {
        alerts.push({
            severity: 'success',
            icon: <SuccessIcon />,
            message: 'Allocation successful - System ready',
        });
    }

    return (
        <WidgetContainer
            title="System Alerts"
            sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
            }}
        >
            {alerts.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4, color: '#6b7280', flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Typography variant="body2">No alerts - Waiting for allocation data</Typography>
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