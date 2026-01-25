import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for managing dashboard data
 * @returns {Object} Dashboard data and loading state
 */
const useDashboardData = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchDashboardData = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch('/api/dashboard/summary');

            if (!response.ok) {
                console.error('Failed to fetch dashboard data:', response.status, response.statusText);

                if (process.env.NODE_ENV === 'development') {
                    console.error('Response details:', {
                        status: response.status,
                        statusText: response.statusText,
                        url: response.url
                    });
                }
                // eslint-disable-next-line no-throw-literal
                throw new Error('Failed to fetch dashboard data');
            }

            const dashboardData = await response.json();
            setData(dashboardData);

        } catch (err) {
            console.error('Error fetching dashboard:', err);

            if (process.env.NODE_ENV === 'development') {
                console.error('Full error details:', {
                    message: err instanceof Error ? err.message : 'Unknown error',
                    stack: err instanceof Error ? err.stack : undefined
                });
            }

            setError(err instanceof Error ? err.message : 'Unknown error');

            // Fallback mock data for development
            setData({
                assignment_status: [
                    { practicum_type: "PDP I", demand_slots: 50, assigned_slots: 50, unassigned_slots: 0 },
                    { practicum_type: "PDP II", demand_slots: 45, assigned_slots: 45, unassigned_slots: 0 },
                    { practicum_type: "SFP", demand_slots: 60, assigned_slots: 58, unassigned_slots: 2 },
                    { practicum_type: "ZSP", demand_slots: 55, assigned_slots: 55, unassigned_slots: 0 },
                ],
                budget_summary: {
                    total_budget: 210,
                    distributed_gs: 169.0,
                    distributed_ms: 41.0,
                    total_distributed: 210.0,
                    remaining_budget: 0.0
                },
                entity_counts: {
                    total_students: 1023,
                    unplaced_students: 12,
                    active_pls_total: 210,
                    active_pls_gs: 169,
                    active_pls_ms: 41,
                    unplaced_students_gs: 8,
                    unplaced_students_ms: 4,
                    active_schools_total: 45,
                    active_schools_gs: 20,
                    active_schools_ms: 15,
                    active_schools_gms: 10
                }
            });
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchDashboardData();
    }, [fetchDashboardData]);

    return {
        data,
        loading,
        error,
        refetch: fetchDashboardData,
    };
};

export default useDashboardData;