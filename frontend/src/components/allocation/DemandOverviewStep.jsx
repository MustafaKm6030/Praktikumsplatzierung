import React, { useState, useMemo, useEffect, useCallback } from 'react';
import { Box, Typography, Grid, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Alert } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { School, Person, CalendarToday, EventAvailable, ArrowForward} from '@mui/icons-material';
import KPICard from '../dashboard/KPICard';
import Button from '../ui/Button';
import Loader from '../ui/Loader';
import allocationService from '../../api/allocationService';
import { getErrorMessage } from '../../api/config';

const formatPracticumType = (type) => {
    const mapping = {
        'PDP_I': 'PDP I',
        'PDP_II': 'PDP II',
        'SFP': 'SFP',
        'ZSP': 'ZSP'
    };
    return mapping[type] || type;
};

const DemandOverviewStep = ({ onComplete }) => {
    const [programFilter, setProgramFilter] = useState('GS');
    const [selectedPracticum, setSelectedPracticum] = useState('ALL');
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchDemandPreview = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await allocationService.getDemandPreview();
            const apiData = response.data;

            const transformedData = {
                summary_cards: {
                    total_demand: apiData.summary_cards.total_demand_slots,
                    pl_capacity: apiData.summary_cards.total_pl_capacity_slots,
                    pdp_slots: apiData.summary_cards.total_pdp_demand,
                    wednesday_slots: apiData.summary_cards.total_wednesday_demand
                },
                detailed_breakdown: apiData.detailed_breakdown.map(item => ({
                    practicum_type: formatPracticumType(item.practicum_type),
                    program_type: item.program_type,
                    subject_display_name: item.subject_display_name,
                    required_slots: item.required_slots,
                    available_pls: item.available_pls
                }))
            };

            setData(transformedData);
        } catch (err) {
            console.error('Error fetching demand preview:', err);
            setError(getErrorMessage(err));
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchDemandPreview();
    }, [fetchDemandPreview]);

    const programData = useMemo(() => {
        if (!data) return [];
        return data.detailed_breakdown.filter(item => item.program_type === programFilter);
    }, [data, programFilter]);

    // 2. Aggregate Data for the Bar Chart
    const chartData = useMemo(() => {
        const aggregation = {};
        programData.forEach(item => {
            if (!aggregation[item.practicum_type]) {
                aggregation[item.practicum_type] = { name: item.practicum_type, value: 0 };
            }
            aggregation[item.practicum_type].value += item.required_slots;
        });
        return Object.values(aggregation);
    }, [programData]);

    // 3. Filter Table Data based on Chart Selection
    const tableData = useMemo(() => {
        if (selectedPracticum === 'ALL') return programData;
        return programData.filter(item => item.practicum_type === selectedPracticum);
    }, [programData, selectedPracticum]);

    // Color logic for the table availability
    const getAvailabilityColor = (req, avail) => {
        if (avail >= req) return '#10b981'; // Green (Enough)
        if (avail >= req * 0.8) return '#F59E0B'; // Yellow (Tight)
        return '#dc2626'; // Red (Shortage)
    };

    if (loading) {
        return <Loader message="Loading demand overview..." />;
    }

    if (error) {
        return (
            <Box>
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
                <Button onClick={fetchDemandPreview}>
                    Retry
                </Button>
            </Box>
        );
    }

    if (!data) {
        return (
            <Alert severity="warning">
                No data available
            </Alert>
        );
    }

    return (
        <Box>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: '#374151' }}>
                System Capacity Snapshot
            </Typography>
            <Grid container spacing={2} sx={{ mb: 4 }}>
                <Grid item xs={12} md={3}>
                    <KPICard label="Total Demand" value={data.summary_cards.total_demand} icon={<Person />} color="#3b82f6" />
                </Grid>
                <Grid item xs={12} md={3}>
                    <KPICard label="PL Capacity" value={data.summary_cards.pl_capacity} icon={<School />} color="#8b5cf6" />
                </Grid>
                <Grid item xs={12} md={3}>
                    <KPICard label="Block PLs" value={data.summary_cards.pdp_slots} icon={<CalendarToday />} color="#F8971C" />
                </Grid>
                <Grid item xs={12} md={3}>
                    <KPICard label="Wednesday PLs" value={data.summary_cards.wednesday_slots} icon={<EventAvailable />} color="#10b981" />
                </Grid>
            </Grid>

            {/* --- SECTION 2: INTERACTIVE FILTERS --- */}
            <Paper sx={{ p: 3, borderRadius: '16px', mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>Demand Distribution</Typography>
                    
                    {/* GS/MS Toggle */}
                    <Box sx={{ bgcolor: '#f3f4f6', p: 0.5, borderRadius: '8px', display: 'flex' }}>
                        {['GS', 'MS'].map((type) => (
                            <Box
                                key={type}
                                onClick={() => { setProgramFilter(type); setSelectedPracticum('ALL'); }}
                                sx={{
                                    px: 3, py: 0.5,
                                    borderRadius: '6px',
                                    cursor: 'pointer',
                                    fontWeight: 600,
                                    fontSize: '14px',
                                    bgcolor: programFilter === type ? 'white' : 'transparent',
                                    color: programFilter === type ? '#F8971C' : '#6b7280',
                                    boxShadow: programFilter === type ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                                    transition: 'all 0.2s'
                                }}
                            >
                                {type}
                            </Box>
                        ))}
                    </Box>
                </Box>

                <Grid container spacing={4}>
                    {/* LEFT: Bar Chart */}
                    <Grid item xs={12} md={5}>
                        <Typography variant="subtitle2" sx={{ mb: 2, color: '#6b7280', textAlign: 'center' }}>
                            Demand by Praktikum Type ({programFilter})
                        </Typography>
                        <ResponsiveContainer width="100%" height={250}>
                            <BarChart data={chartData} onClick={(data) => data && setSelectedPracticum(data.activePayload[0].payload.name)}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                                <YAxis />
                                <Tooltip cursor={{ fill: '#f3f4f6' }} />
                                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                                    {chartData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={selectedPracticum === entry.name ? '#F8971C' : '#3b82f6'} cursor="pointer" />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                        <Typography variant="caption" sx={{ display: 'block', textAlign: 'center', mt: 1, color: '#9ca3af' }}>
                            * Click a bar to filter the table
                        </Typography>
                    </Grid>

                    {/* RIGHT: Detailed Table */}
                    <Grid item xs={12} md={7}>
                        <Typography variant="subtitle2" sx={{ mb: 2, color: '#6b7280' }}>
                            Subject Breakdown: {selectedPracticum === 'ALL' ? 'All Types' : selectedPracticum}
                        </Typography>
                        <TableContainer sx={{ maxHeight: 250 }}>
                            <Table size="small" stickyHeader>
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Subject</TableCell>
                                        <TableCell>Type</TableCell>
                                        <TableCell align="right">Demand</TableCell>
                                        <TableCell align="right">Supply (PLs)</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {tableData.map((row, index) => (
                                        <TableRow key={index} hover>
                                            <TableCell sx={{ fontWeight: 500 }}>{row.subject_display_name}</TableCell>
                                            <TableCell><Chip label={row.practicum_type} size="small" /></TableCell>
                                            <TableCell align="right">{row.required_slots}</TableCell>
                                            <TableCell align="right" sx={{ fontWeight: 700, color: getAvailabilityColor(row.required_slots, row.available_pls) }}>
                                                {row.available_pls}
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Grid>
                </Grid>
            </Paper>

            {/* Navigation */}
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 4 }}>
                <Button onClick={onComplete} size="large" endIcon={<ArrowForward />}>
                    Continue to Auto-Allocation
                </Button>
            </Box>
        </Box>
    );
};

export default DemandOverviewStep;