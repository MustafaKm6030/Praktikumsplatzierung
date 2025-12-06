import React, { useState } from 'react';
import { 
    Box, Typography, Paper, Table, TableBody, TableCell, 
    TableContainer, TableHead, TableRow, Chip, Stack 
} from '@mui/material';
import { 
    CheckCircle, Warning, Edit as EditIcon, 
    ArrowForward, FilterList 
} from '@mui/icons-material';
import Button from '../ui/Button';
import TextField from '../ui/TextField';

// Mock Data
const MOCK_RESULTS = [
    { id: '0000001', name: 'Anna Müller', type: 'PDP I', subject: 'Deutsch', pl: 'PL Weber', status: 'ok' },
    { id: '0000002', name: 'Laura Hamert', type: 'PDP I', subject: 'Deutsch', pl: 'PL Weber', status: 'ok' },
    { id: '0000003', name: 'Anna Mohnenn', type: 'SFP', subject: 'Deutsch', pl: 'PL Crotorrhuren', status: 'ok' },
    { id: '0000003', name: 'Anna Müller', type: 'SFP', subject: 'Deutsch', pl: 'PL Weber', status: 'conflict', issue: 'Potential Conflict' },
    { id: '0000004', name: 'Maria Hamerz', type: 'PDP I', subject: 'Deutsch', pl: 'PL Weber', status: 'ok' },
    { id: '0000005', name: 'Stefan Verkerz', type: 'PDP I', subject: 'Film', pl: 'PL Weber', status: 'ok' },
];

const AllocationResultsStep = ({ onComplete }) => {
    const [searchTerm, setSearchTerm] = useState('');

    const handleManualAdjust = (studentId) => {
        alert(`Manual Adjustment for ${studentId} - Feature coming in Sprint 4`);
    };

    return (
        <Box>
            {/* Header & Filter */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Box>
                    <Typography variant="h5" sx={{ fontWeight: 700, color: '#1f2937' }}>
                        Draft Allocation Review
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#6b7280' }}>
                        Visualize and adjust generated assignments.
                    </Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button variant="secondary" startIcon={<FilterList />}>Filter</Button>
                    <TextField 
                        placeholder="Search..." 
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        sx={{ width: 250 }}
                        size="small"
                    />
                </Box>
            </Box>

            {/* Results Table */}
            <TableContainer component={Paper} sx={{ borderRadius: '12px', boxShadow: '0 2px 10px rgba(0,0,0,0.08)', mb: 4 }}>
                <Table>
                    <TableHead sx={{ bgcolor: '#f9fafb' }}>
                        <TableRow>
                            <TableCell><strong>Student ID</strong></TableCell>
                            <TableCell><strong>Name</strong></TableCell>
                            <TableCell><strong>Praktikum Type</strong></TableCell>
                            <TableCell><strong>Subject</strong></TableCell>
                            <TableCell><strong>Allocated PL</strong></TableCell>
                            <TableCell><strong>Status</strong></TableCell>
                            <TableCell align="right"><strong>Actions</strong></TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {MOCK_RESULTS.map((row, index) => (
                            <TableRow key={index} hover>
                                <TableCell sx={{ fontFamily: 'monospace', color: '#6b7280' }}>{row.id}</TableCell>
                                <TableCell sx={{ fontWeight: 500 }}>{row.name}</TableCell>
                                <TableCell>
                                    <Chip label={row.type} size="small" sx={{ bgcolor: '#e0f2fe', color: '#0369a1', fontWeight: 600 }} />
                                </TableCell>
                                <TableCell>{row.subject}</TableCell>
                                <TableCell>{row.pl}</TableCell>
                                <TableCell>
                                    {row.status === 'ok' ? (
                                        <CheckCircle sx={{ color: '#10b981' }} />
                                    ) : (
                                        <Stack direction="row" spacing={1} alignItems="center">
                                            <Warning sx={{ color: '#F59E0B' }} />
                                            <Typography variant="caption" sx={{ color: '#d97706', fontWeight: 600 }}>
                                                {row.issue}
                                            </Typography>
                                        </Stack>
                                    )}
                                </TableCell>
                                <TableCell align="right">
                                    <Button 
                                        variant="secondary" 
                                        size="small" 
                                        onClick={() => handleManualAdjust(row.id)}
                                        startIcon={<EditIcon sx={{ fontSize: 16 }} />}
                                    >
                                        Adjust
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>

            {/* Navigation Footer */}
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', pt: 2 }}>
                <Button 
                    onClick={onComplete} 
                    size="large" 
                    endIcon={<ArrowForward />}
                >
                    Finalize & Generate Reports
                </Button>
            </Box>
        </Box>
    );
};

export default AllocationResultsStep;