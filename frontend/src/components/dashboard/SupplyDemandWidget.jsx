import React from 'react';
import { Typography, Grid } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import KPICard from './KPICard';
import WidgetContainer from './WidgetContainer';
import { People as PeopleIcon, School as StudentIcon, WarningAmber as WarningIcon } from '@mui/icons-material';

/**
 * Widget 3:
 * PL & Student Demand
 * Shows supply vs demand balance
 */
const SupplyDemandWidget = ({ data = {} }) => {
    const {
        active_pls_total = 0,
        total_students = 0,
        unplaced_students = 0,
        active_pls_gs = 0,
        active_pls_ms = 0,
        unplaced_students_gs = 0,
        unplaced_students_ms = 0,
    } = data;

    const plData = [
        { name: 'GS', value: active_pls_gs },
        { name: 'MS', value: active_pls_ms },
    ];

    const unplacedStudentData = [
        { name: 'GS', value: unplaced_students_gs },
        { name: 'MS', value: unplaced_students_ms },
    ];

    const placedStudentData = [
        { name: 'GS', value: (total_students - unplaced_students) - unplaced_students_ms },
        { name: 'MS', value: total_students - unplaced_students - ((total_students - unplaced_students) - unplaced_students_ms) },
    ];

    return (
        <WidgetContainer>
            {/* Top KPIs */}
            <Grid container spacing={2} sx={{ mb: 3 }} >
                <Grid item xs={12} md={4}>
                    <KPICard
                        label="Active PLs"
                        value={active_pls_total}
                        icon={<PeopleIcon />}
                        color="#8b5cf6"
                    />
                </Grid>
                <Grid item xs={12} md={4}>
                    <KPICard
                        label="Total Students"
                        value={total_students}
                        icon={<StudentIcon />}
                        color="#3b82f6"
                    />
                </Grid>
                <Grid item xs={12} md={4}>
                    <KPICard
                        label="Unplaced Students"
                        value={unplaced_students}
                        icon={<WarningIcon />}
                        color={unplaced_students > 0 ? '#dc2626' : '#10b981'}
                    />
                </Grid>
            </Grid>

            {/* Bottom Charts */}
            <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#1f2937', mb: 2 }}>
                        PL Supply (GS vs MS)
                    </Typography>
                    <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={plData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="value" fill="#8b5cf6" />
                        </BarChart>
                    </ResponsiveContainer>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#1f2937', mb: 2 }}>
                        Placed Students (GS vs MS)
                    </Typography>
                    <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={placedStudentData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="value" fill="#10b981" />
                        </BarChart>
                    </ResponsiveContainer>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#1f2937', mb: 2 }}>
                        Unplaced Students (GS vs MS)
                    </Typography>
                    <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={unplacedStudentData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="value" fill="#dc2626" />
                        </BarChart>
                    </ResponsiveContainer>
                </Grid>
            </Grid>
        </WidgetContainer>
    );
};

export default SupplyDemandWidget;