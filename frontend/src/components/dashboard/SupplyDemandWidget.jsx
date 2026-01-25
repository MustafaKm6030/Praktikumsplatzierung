import React from 'react';
import { Typography, Grid } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import KPICard from './KPICard';
import WidgetContainer from './WidgetContainer';
import { People as PeopleIcon, School as StudentIcon, School as SchoolIcon } from '@mui/icons-material';

/**
 * Widget 3:
 * PL & Student Demand
 * Shows supply vs demand balance
 */
const SupplyDemandWidget = ({ data = {} }) => {
    const {
        active_pls_total = 0,
        total_students = 0,
        active_pls_gs = 0,
        active_pls_ms = 0,
        total_students_gs = 0,
        total_students_ms = 0,
        active_schools_total = 0,
        active_schools_gs = 0,
        active_schools_ms = 0,
        active_schools_gms = 0,
    } = data;

    const plData = [
        { name: 'GS', value: active_pls_gs },
        { name: 'MS', value: active_pls_ms },
    ];

    const studentData = [
        { name: 'GS', value: total_students_gs },
        { name: 'MS', value: total_students_ms },
    ];

    const activeSchoolsData = [
        { name: 'GS', value: active_schools_gs },
        { name: 'MS', value: active_schools_ms },
        { name: 'Beide', value: active_schools_gms },
    ];

    return (
        <WidgetContainer>
            {/* Top KPIs */}
            <Grid container spacing={2} sx={{ mb: 3 }} >
                <Grid item xs={12} md={4}>
                    <KPICard
                        label="Aktive Praktikumslehrkräfte"
                        value={active_pls_total}
                        icon={<PeopleIcon />}
                        color="#8b5cf6"
                    />
                </Grid>
                <Grid item xs={12} md={4}>
                    <KPICard
                        label="Studierende gesamt"
                        value={total_students}
                        icon={<StudentIcon />}
                        color="#3b82f6"
                    />
                </Grid>
                <Grid item xs={12} md={4}>
                    <KPICard
                        label="Aktive Schulen"
                        value={active_schools_total}
                        icon={<SchoolIcon />}
                        color="#10b981"
                    />
                </Grid>
            </Grid>

            {/* Bottom Charts */}
            <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#1f2937', mb: 2 }}>
                        Praktikumslehrkräfte-Angebot (GS vs MS)
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
                        Studierende gesamt (GS vs MS)
                    </Typography>
                    <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={studentData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="value" fill="#3b82f6" />
                        </BarChart>
                    </ResponsiveContainer>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#1f2937', mb: 2 }}>
                        Aktive Schulen (GS, MS, Beide)
                    </Typography>
                    <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={activeSchoolsData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="value" fill="#10b981" />
                        </BarChart>
                    </ResponsiveContainer>
                </Grid>
            </Grid>
        </WidgetContainer>
    );
};

export default SupplyDemandWidget;