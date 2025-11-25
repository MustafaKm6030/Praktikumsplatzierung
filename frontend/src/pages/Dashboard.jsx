import React from 'react';
import { Box, Grid } from '@mui/material';
import PraktikaStatusWidget from '../components/dashboard/PraktikaStatusWidget';
import SupplyDemandWidget from '../components/dashboard/SupplyDemandWidget';
import SystemAlertsWidget from '../components/dashboard/SystemAlertsWidget';
import useDashboardData from '../components/dashboard/useDashboardData';
import Loader from '../components/ui/Loader';

function Dashboard() {
    const { data, loading, refetch } = useDashboardData();

    if (loading) {
        return (
            <Box sx={{ minHeight: '100vh', backgroundColor: '#f1f1f1', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Loader message="Loading dashboard..." />
            </Box>
        );
    }

    return (
        <Box sx={{
            minHeight: '100vh',
            backgroundColor: '#f1f1f1',
            pt: '40px',  // Match layout-content top margin
            px: '16px',  // Match layout-content side margins
            pb: 2
        }}>
            <Grid container spacing={2}>
                {/* Widget 3: Supply Demand - Full Width Top */}
                <Grid item xs={12}>
                    <SupplyDemandWidget
                        data={data?.entity_counts || {}}
                        onRefresh={refetch}
                    />
                </Grid>

                {/* Widget 1: Praktika Status */}
                <Grid item xs={12} lg={8}>
                    <PraktikaStatusWidget data={data?.assignment_status || []} />
                </Grid>

                {/* Widget 4: System Alerts */}
                <Grid item xs={12} lg={4}>
                    <SystemAlertsWidget
                        assignmentStatus={data?.assignment_status || []}
                        budgetSummary={data?.budget_summary || {}}
                        entityCounts={data?.entity_counts || {}}
                    />
                </Grid>
            </Grid>
        </Box>
    );
}

export default Dashboard;