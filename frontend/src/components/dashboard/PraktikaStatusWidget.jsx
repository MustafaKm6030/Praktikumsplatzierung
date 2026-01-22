import React from 'react';
import { Box, Typography } from '@mui/material';
import WidgetContainer from './WidgetContainer';

/**
 * Widget 1: Student Summary Overview
 * Shows total students, assigned, and unassigned students in a compact info box
 */
const PraktikaStatusWidget = ({ data = {} }) => {
    const { total_students = 0, assigned_students = 0, unassigned_students = 0 } = data;
    
    return (
        <WidgetContainer>
            <Box
                sx={{
                    display: 'flex',
                    alignItems: 'stretch',
                    backgroundColor: '#fef9f3',
                    borderRadius: '12px',
                    overflow: 'hidden',
                    minHeight: '100px',
                }}
            >
                {/* Total Students */}
                <Box
                    sx={{
                        flex: 1,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        padding: '20px',
                        borderRight: '2px solid #e5e7eb',
                    }}
                >
                    <Typography
                        variant="body2"
                        sx={{
                            color: '#6b7280',
                            fontWeight: 500,
                            marginBottom: '8px',
                            textTransform: 'uppercase',
                            fontSize: '0.75rem',
                            letterSpacing: '0.5px',
                        }}
                    >
                        Gesamt Studenten
                    </Typography>
                    <Typography
                        variant="h3"
                        sx={{
                            fontWeight: 700,
                            color: '#1f2937',
                        }}
                    >
                        {total_students}
                    </Typography>
                </Box>

                {/* Assigned Students */}
                <Box
                    sx={{
                        flex: 1,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        padding: '20px',
                        borderRight: '2px solid #e5e7eb',
                    }}
                >
                    <Typography
                        variant="body2"
                        sx={{
                            color: '#6b7280',
                            fontWeight: 500,
                            marginBottom: '8px',
                            textTransform: 'uppercase',
                            fontSize: '0.75rem',
                            letterSpacing: '0.5px',
                        }}
                    >
                        Zugewiesen
                    </Typography>
                    <Typography
                        variant="h3"
                        sx={{
                            fontWeight: 700,
                            color: '#10b981',
                        }}
                    >
                        {assigned_students}
                    </Typography>
                </Box>

                {/* Unassigned Students */}
                <Box
                    sx={{
                        flex: 1,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        padding: '20px',
                    }}
                >
                    <Typography
                        variant="body2"
                        sx={{
                            color: '#6b7280',
                            fontWeight: 500,
                            marginBottom: '8px',
                            textTransform: 'uppercase',
                            fontSize: '0.75rem',
                            letterSpacing: '0.5px',
                        }}
                    >
                        Nicht zugewiesen
                    </Typography>
                    <Typography
                        variant="h3"
                        sx={{
                            fontWeight: 700,
                            color: unassigned_students > 0 ? '#dc2626' : '#6b7280',
                        }}
                    >
                        {unassigned_students}
                    </Typography>
                </Box>
            </Box>
        </WidgetContainer>
    );
};

export default PraktikaStatusWidget;