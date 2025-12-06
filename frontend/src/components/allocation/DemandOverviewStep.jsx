import React, { useState, useMemo } from 'react';
import { Box, Typography, Grid, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { School, Person, CalendarToday, EventAvailable, ArrowForward} from '@mui/icons-material';
import KPICard from '../dashboard/KPICard';
import Button from '../ui/Button';

// --- MOCK DATA ---
const MOCK_DATA = {
    summary_cards: {
        total_demand: 210,
        pl_capacity: 220,
        pdp_slots: 95,
        wednesday_slots: 115
    },
    // Detailed breakdown used for charts and tables
    detailed_breakdown: [
        { practicum_type: "PDP I", program_type: "GS", subject_display_name: "General", required_slots: 50, available_pls: 55 },
        { practicum_type: "PDP I", program_type: "MS", subject_display_name: "General", required_slots: 15, available_pls: 12 },
        { practicum_type: "PDP II", program_type: "GS", subject_display_name: "General", required_slots: 45, available_pls: 48 },
        { practicum_type: "SFP", program_type: "GS", subject_display_name: "Deutsch", required_slots: 35, available_pls: 30 },
        { practicum_type: "SFP", program_type: "GS", subject_display_name: "Mathe", required_slots: 29, available_pls: 30 },
        { practicum_type: "SFP", program_type: "MS", subject_display_name: "Englisch", required_slots: 12, available_pls: 10 },
        { practicum_type: "ZSP", program_type: "GS", subject_display_name: "HSU", required_slots: 20, available_pls: 20 },
        { practicum_type: "ZSP", program_type: "MS", subject_display_name: "Sport", required_slots: 8, available_pls: 8 },
    ]
};

const DemandOverviewStep = ({ onComplete }) => {
    const [programFilter, setProgramFilter] = useState('GS'); // 'GS' or 'MS'
    const [selectedPracticum, setSelectedPracticum] = useState('ALL'); // 'ALL', 'PDP I', etc.

    // 1. Filter Data based on Program (GS/MS)
    const programData = useMemo(() => {
        return MOCK_DATA.detailed_breakdown.filter(item => item.program_type === programFilter);
    }, [programFilter]);

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

    return (
        <Box>
            {/* --- SECTION 1: SUMMARY CARDS --- */}
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: '#374151' }}>
                System Capacity Snapshot
            </Typography>
            <Grid container spacing={2} sx={{ mb: 4 }}>
                <Grid item xs={12} md={3}>
                    <KPICard label="Total Demand" value={MOCK_DATA.summary_cards.total_demand} icon={<Person />} color="#3b82f6" />
                </Grid>
                <Grid item xs={12} md={3}>
                    <KPICard label="PL Capacity" value={MOCK_DATA.summary_cards.pl_capacity} icon={<School />} color="#8b5cf6" />
                </Grid>
                <Grid item xs={12} md={3}>
                    <KPICard label="PDP Slots (Block)" value={MOCK_DATA.summary_cards.pdp_slots} icon={<CalendarToday />} color="#F8971C" />
                </Grid>
                <Grid item xs={12} md={3}>
                    <KPICard label="Wed. Slots" value={MOCK_DATA.summary_cards.wednesday_slots} icon={<EventAvailable />} color="#10b981" />
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