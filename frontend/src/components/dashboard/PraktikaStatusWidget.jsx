import React from 'react';
import { Box, Typography } from '@mui/material';
import { Groups as StudentsIcon, CheckCircle as AssignedIcon, RemoveCircle as UnassignedIcon } from '@mui/icons-material';
import WidgetContainer from './WidgetContainer';

/**
 * Widget 1: Student Summary Overview
 * Shows total students, assigned, and unassigned students with circular progress indicator
 */
const PraktikaStatusWidget = ({ data = {} }) => {
    const { total_students = 0, assigned_students = 0, unassigned_students = 0 } = data;
    
    // Calculate percentage for circular progress
    const percentage = total_students > 0 ? Math.round((assigned_students / total_students) * 100) : 0;
    
    // Circle parameters
    const radius = 70;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (percentage / 100) * circumference;
    
    return (
        <WidgetContainer
            sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
            }}
        >
            <Box
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 4,
                    height: '100%',
                    padding: '12px',
                }}
            >
                {/* Left: Circular Progress */}
                <Box
                    sx={{
                        position: 'relative',
                        width: '180px',
                        height: '180px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                    }}
                >
                    {/* SVG Circle */}
                    <svg
                        width="180"
                        height="180"
                        style={{ transform: 'rotate(-90deg)' }}
                    >
                        {/* Background circle */}
                        <circle
                            cx="90"
                            cy="90"
                            r={radius}
                            fill="none"
                            stroke="#e5e7eb"
                            strokeWidth="12"
                        />
                        {/* Progress circle */}
                        <circle
                            cx="90"
                            cy="90"
                            r={radius}
                            fill="none"
                            stroke={percentage === 100 ? '#10b981' : percentage >= 50 ? '#3b82f6' : '#f59e0b'}
                            strokeWidth="12"
                            strokeDasharray={circumference}
                            strokeDashoffset={strokeDashoffset}
                            strokeLinecap="round"
                            style={{
                                transition: 'stroke-dashoffset 1s ease-in-out, stroke 0.3s ease',
                            }}
                        />
                    </svg>
                    
                    {/* Center text */}
                    <Box
                        sx={{
                            position: 'absolute',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}
                    >
                        <Typography
                            variant="h2"
                            sx={{
                                fontWeight: 800,
                                color: percentage === 100 ? '#10b981' : percentage >= 50 ? '#3b82f6' : '#f59e0b',
                                fontSize: '2.5rem',
                                lineHeight: 1,
                            }}
                        >
                            {percentage}%
                        </Typography>
                        <Typography
                            variant="caption"
                            sx={{
                                color: '#6b7280',
                                fontWeight: 600,
                                fontSize: '0.7rem',
                                marginTop: '4px',
                                textTransform: 'uppercase',
                                letterSpacing: '0.5px',
                            }}
                        >
                            Zugewiesen
                        </Typography>
                    </Box>
                </Box>

                {/* Right: Stats Cards */}
                <Box
                    sx={{
                        flex: 1,
                        display: 'flex',
                        flexDirection: 'column',
                        gap: 2,
                        height: '100%',
                        justifyContent: 'center',
                    }}
                >
                    {/* Total Students */}
                    <Box
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 2,
                            padding: '16px 20px',
                            backgroundColor: '#f8fafc',
                            borderRadius: '12px',
                            border: '1px solid #e2e8f0',
                        }}
                    >
                        <Box
                            sx={{
                                width: '48px',
                                height: '48px',
                                borderRadius: '12px',
                                backgroundColor: '#3b82f6',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                            }}
                        >
                            <StudentsIcon sx={{ color: '#ffffff', fontSize: '28px' }} />
                        </Box>
                        <Box sx={{ flex: 1 }}>
                            <Typography
                                variant="caption"
                                sx={{
                                    color: '#64748b',
                                    fontWeight: 600,
                                    fontSize: '0.7rem',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.5px',
                                }}
                            >
                                Gesamt Studenten
                            </Typography>
                            <Typography
                                variant="h4"
                                sx={{
                                    fontWeight: 700,
                                    color: '#1e293b',
                                    lineHeight: 1.2,
                                }}
                            >
                                {total_students}
                            </Typography>
                        </Box>
                    </Box>

                    {/* Assigned Students */}
                    <Box
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 2,
                            padding: '16px 20px',
                            backgroundColor: '#f0fdf4',
                            borderRadius: '12px',
                            border: '1px solid #bbf7d0',
                        }}
                    >
                        <Box
                            sx={{
                                width: '48px',
                                height: '48px',
                                borderRadius: '12px',
                                backgroundColor: '#10b981',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                            }}
                        >
                            <AssignedIcon sx={{ color: '#ffffff', fontSize: '28px' }} />
                        </Box>
                        <Box sx={{ flex: 1 }}>
                            <Typography
                                variant="caption"
                                sx={{
                                    color: '#15803d',
                                    fontWeight: 600,
                                    fontSize: '0.7rem',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.5px',
                                }}
                            >
                                Zugewiesen
                            </Typography>
                            <Typography
                                variant="h4"
                                sx={{
                                    fontWeight: 700,
                                    color: '#15803d',
                                    lineHeight: 1.2,
                                }}
                            >
                                {assigned_students}
                            </Typography>
                        </Box>
                    </Box>

                    {/* Unassigned Students */}
                    <Box
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 2,
                            padding: '16px 20px',
                            backgroundColor: unassigned_students > 0 ? '#fef2f2' : '#f8fafc',
                            borderRadius: '12px',
                            border: `1px solid ${unassigned_students > 0 ? '#fecaca' : '#e2e8f0'}`,
                        }}
                    >
                        <Box
                            sx={{
                                width: '48px',
                                height: '48px',
                                borderRadius: '12px',
                                backgroundColor: unassigned_students > 0 ? '#ef4444' : '#94a3b8',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                            }}
                        >
                            <UnassignedIcon sx={{ color: '#ffffff', fontSize: '28px' }} />
                        </Box>
                        <Box sx={{ flex: 1 }}>
                            <Typography
                                variant="caption"
                                sx={{
                                    color: unassigned_students > 0 ? '#991b1b' : '#64748b',
                                    fontWeight: 600,
                                    fontSize: '0.7rem',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.5px',
                                }}
                            >
                                Nicht zugewiesen
                            </Typography>
                            <Typography
                                variant="h4"
                                sx={{
                                    fontWeight: 700,
                                    color: unassigned_students > 0 ? '#991b1b' : '#64748b',
                                    lineHeight: 1.2,
                                }}
                            >
                                {unassigned_students}
                            </Typography>
                        </Box>
                    </Box>
                </Box>
            </Box>
        </WidgetContainer>
    );
};

export default PraktikaStatusWidget;