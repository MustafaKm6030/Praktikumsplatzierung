import React, { useState, useEffect } from 'react';
import { 
    Box, Typography, Paper, Table, TableBody, TableCell, 
    TableContainer, TableHead, TableRow, Chip, Stack, CircularProgress, Alert
} from '@mui/material';
import { 
    CheckCircle, Warning, Edit as EditIcon, 
    ArrowForward, FilterList 
} from '@mui/icons-material';
import Button from '../ui/Button';
import TextField from '../ui/TextField';
import allocationService from '../../api/allocationService';

const AllocationResultsStep = ({ onComplete }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [assignments, setAssignments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchAssignments();
    }, []);

    const fetchAssignments = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await allocationService.getAssignments();
            setAssignments(response.data || []);
        } catch (err) {
            console.error('Failed to fetch assignments:', err);
            setError(err.message || 'Failed to load assignments');
        } finally {
            setLoading(false);
        }
    };

    const handleManualAdjust = (assignmentId) => {
        alert(`Manual Adjustment for Assignment ${assignmentId} - Feature coming in Sprint 4`);
    };

    const filteredAssignments = assignments.filter(assignment => {
        const searchLower = searchTerm.toLowerCase();
        return (
            (assignment.mentor_name && assignment.mentor_name.toLowerCase().includes(searchLower)) ||
            (assignment.practicum_type && assignment.practicum_type.toLowerCase().includes(searchLower)) ||
            (assignment.subject && assignment.subject.toLowerCase().includes(searchLower)) ||
            (assignment.school_name && assignment.school_name.toLowerCase().includes(searchLower))
        );
    });

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
            {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
                    <CircularProgress />
                </Box>
            ) : error ? (
                <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                </Alert>
            ) : (
                <TableContainer component={Paper} sx={{ borderRadius: '12px', boxShadow: '0 2px 10px rgba(0,0,0,0.08)', mb: 4 }}>
                    <Table>
                        <TableHead sx={{ bgcolor: '#f9fafb' }}>
                            <TableRow>
                                <TableCell><strong>Assignment ID</strong></TableCell>
                                <TableCell><strong>Mentor</strong></TableCell>
                                <TableCell><strong>Praktikum Type</strong></TableCell>
                                <TableCell><strong>Subject</strong></TableCell>
                                <TableCell><strong>School</strong></TableCell>
                                <TableCell><strong>Status</strong></TableCell>
                                <TableCell align="right"><strong>Actions</strong></TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {filteredAssignments.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={7} align="center" sx={{ py: 4, color: '#6b7280' }}>
                                        {searchTerm ? 'No assignments match your search.' : 'No assignments found. Run the allocation algorithm first.'}
                                    </TableCell>
                                </TableRow>
                            ) : (
                                filteredAssignments.map((assignment) => (
                                    <TableRow key={assignment.id} hover>
                                        <TableCell sx={{ fontFamily: 'monospace', color: '#6b7280' }}>
                                            #{assignment.id}
                                        </TableCell>
                                        <TableCell sx={{ fontWeight: 500 }}>
                                            {assignment.mentor_name || 'N/A'}
                                        </TableCell>
                                        <TableCell>
                                            <Chip 
                                                label={assignment.practicum_type || 'N/A'} 
                                                size="small" 
                                                sx={{ bgcolor: '#e0f2fe', color: '#0369a1', fontWeight: 600 }} 
                                            />
                                        </TableCell>
                                        <TableCell>{assignment.subject || 'N/A'}</TableCell>
                                        <TableCell>{assignment.school_name || 'N/A'}</TableCell>
                                        <TableCell>
                                            {assignment.status === 'ok' ? (
                                                <CheckCircle sx={{ color: '#10b981' }} />
                                            ) : (
                                                <Stack direction="row" spacing={1} alignItems="center">
                                                    <Warning sx={{ color: '#F59E0B' }} />
                                                    <Typography variant="caption" sx={{ color: '#d97706', fontWeight: 600 }}>
                                                        {assignment.issue || 'Issue'}
                                                    </Typography>
                                                </Stack>
                                            )}
                                        </TableCell>
                                        <TableCell align="right">
                                            <Button 
                                                variant="secondary" 
                                                size="small" 
                                                onClick={() => handleManualAdjust(assignment.id)}
                                                startIcon={<EditIcon sx={{ fontSize: 16 }} />}
                                            >
                                                Adjust
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
            )}

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