import React, { useState, useEffect } from 'react';
import {
    Box, Typography, Paper, Table, TableBody, TableCell,
    TableContainer, TableHead, TableRow, Chip, Stack, CircularProgress, Alert,
    Dialog, DialogTitle, DialogContent, DialogActions, TablePagination, Select, MenuItem, FormControl, Grid
} from '@mui/material';
import {
    CheckCircle, Warning, Edit as EditIcon,
    ArrowForward, FilterList, DeleteForever, Cancel
} from '@mui/icons-material';
import Button from '../ui/Button';
import TextField from '../ui/TextField';
import allocationService from '../../api/allocationService';
import AdjustAssignmentDialog from '../assignments/AdjustAssignmentDialog';
import KPICard from '../dashboard/KPICard';

const AllocationResultsStep = ({ onComplete, onReset, solverResults }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [assignments, setAssignments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    // State to track which mentor is being adjusted (opens the modal)
    const [adjustingMentorId, setAdjustingMentorId] = useState(null);
    
    // Pagination state
    const [page, setPage] = useState(0);
    const [rowsPerPage] = useState(25);
    
    // Reset confirmation dialog state
    const [resetDialogOpen, setResetDialogOpen] = useState(false);
    const [resetting, setResetting] = useState(false);

    // Statistics state
    const [stats, setStats] = useState({
        matchRate: '0%',
        totalAssignments: 0,
        unmatchedCount: 0
    });

    useEffect(() => {
        fetchAssignments();
    }, [solverResults]);

    const fetchAssignments = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await allocationService.getAssignments();
            const assignmentData = response.data || [];
            setAssignments(assignmentData);
            
            // Calculate statistics
            // Use solver results if available, otherwise calculate from assignments
            let totalAssigned, totalUnassigned, matchRate;
            
            if (solverResults) {
                totalAssigned = solverResults.total_assignments || 0;
                totalUnassigned = solverResults.total_unassigned || 0;
                const totalMentors = totalAssigned + totalUnassigned;
                matchRate = totalMentors > 0
                    ? Math.round((totalAssigned / totalMentors) * 100)
                    : 0;
            } else {
                totalAssigned = assignmentData.filter(a => a.status === 'ok').length;
                totalUnassigned = assignmentData.filter(a => a.status === 'unallocated').length;
                const totalMentors = totalAssigned + totalUnassigned;
                matchRate = totalMentors > 0
                    ? Math.round((totalAssigned / totalMentors) * 100)
                    : 0;
            }
            
            setStats({
                matchRate: `${matchRate}%`,
                totalAssignments: totalAssigned,
                unmatchedCount: totalUnassigned
            });
        } catch (err) {
            console.error('Failed to fetch assignments:', err);
            setError(err.message || 'Failed to load assignments');
        } finally {
            setLoading(false);
        }
    };

    const handleManualAdjust = (mentorId) => {
        if (!mentorId) {
            console.warn("No Mentor ID found for this row");
            return;
        }
        setAdjustingMentorId(mentorId);
    };

    const handleResetClick = () => {
        setResetDialogOpen(true);
    };

    const handleResetConfirm = async () => {
        try {
            setResetting(true);
            const response = await fetch('/api/assignments/reset/', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (response.ok) {
                await response.json();
                setResetDialogOpen(false);
                setError(null);
                // Navigate back to Bedarfsübersicht (step 0)
                if (onReset) {
                    onReset();
                }
            } else {
                const errData = await response.json();
                setError(errData.error || 'Failed to reset assignments');
            }
        } catch (err) {
            setError('Network error occurred while resetting assignments');
        } finally {
            setResetting(false);
        }
    };

    const handleResetCancel = () => {
        setResetDialogOpen(false);
    };

    // Filter and sort assignments (unallocated first)
    const filteredAssignments = assignments
        .filter(assignment => {
            const searchLower = searchTerm.toLowerCase();
            return (
                (assignment.mentor_name && assignment.mentor_name.toLowerCase().includes(searchLower)) ||
                (assignment.practicum_type && assignment.practicum_type.toLowerCase().includes(searchLower)) ||
                (assignment.subject && assignment.subject.toLowerCase().includes(searchLower)) ||
                (assignment.school_name && assignment.school_name.toLowerCase().includes(searchLower))
            );
        })
        .sort((a, b) => {
            // Sort: unallocated first, then allocated
            if (a.status === 'unallocated' && b.status !== 'unallocated') return -1;
            if (a.status !== 'unallocated' && b.status === 'unallocated') return 1;
            return 0;
        });

    // Paginate filtered assignments
    const paginatedAssignments = filteredAssignments.slice(
        page * rowsPerPage,
        page * rowsPerPage + rowsPerPage
    );

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handlePageJump = (event) => {
        setPage(event.target.value);
    };

    // Calculate total pages
    const totalPages = Math.ceil(filteredAssignments.length / rowsPerPage);

    return (
        <Box>
            {/* Statistics Summary */}
            {!loading && assignments.length > 0 && (
                <>
                    <Typography variant="h5" sx={{ mb: 4, fontWeight: 700, textAlign: 'center' }}>
                        Zuteilungsergebnisse - Zusammenfassung
                    </Typography>

                    <Grid container spacing={3} sx={{ mb: 6 }}>
                        <Grid item xs={12} md={4}>
                            <KPICard
                                label="Erfolgsquote"
                                value={stats.matchRate}
                                icon={<CheckCircle />}
                                color="#10b981"
                            />
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <KPICard
                                label="Gesamtzuweisungen"
                                value={stats.totalAssignments}
                                icon={<CheckCircle />}
                                color="#3b82f6"
                            />
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <KPICard
                                label="Nicht zugewiesene Lehrkräfte"
                                value={stats.unmatchedCount}
                                icon={<Warning />}
                                color="#dc2626"
                            />
                        </Grid>
                    </Grid>
                </>
            )}

            {/* Header & Filter */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Box>
                    <Typography variant="h5" sx={{ fontWeight: 700, color: '#1f2937' }}>
                        Entwurfszuteilung überprüfen
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#6b7280' }}>
                        Generierte Zuweisungen visualisieren und anpassen.
                    </Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button 
                        variant="secondary" 
                        startIcon={<DeleteForever />}
                        onClick={handleResetClick}
                        sx={{ 
                            color: '#dc2626', 
                            borderColor: '#dc2626',
                            '&:hover': { 
                                bgcolor: '#fef2f2', 
                                borderColor: '#b91c1c' 
                            } 
                        }}
                    >
                        Zurücksetzen
                    </Button>
                    <Button variant="secondary" startIcon={<FilterList />}>Filter</Button>
                    <TextField
                        placeholder="Suchen..."
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
                                <TableCell><strong>Zuweisungs-ID</strong></TableCell>
                                <TableCell><strong>PLs</strong></TableCell>
                                <TableCell><strong>Praktikumstyp</strong></TableCell>
                                <TableCell><strong>Fach</strong></TableCell>
                                <TableCell><strong>Schule</strong></TableCell>
                                <TableCell><strong>Status</strong></TableCell>
                                <TableCell align="right"><strong>Aktionen</strong></TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {filteredAssignments.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={7} align="center" sx={{ py: 4, color: '#6b7280' }}>
                                        {searchTerm ? 'Keine Zuweisungen entsprechen Ihrer Suche.' : 'Keine Zuweisungen gefunden. Führen Sie zuerst den Zuteilungsalgorithmus aus.'}
                                    </TableCell>
                                </TableRow>
                            ) : (
                                paginatedAssignments.map((assignment, index) => (
                                    <TableRow key={assignment.id || `unallocated-${index}`} hover>
                                        <TableCell sx={{ fontFamily: 'monospace', color: '#6b7280' }}>
                                            {assignment.id ? `#${assignment.id}` : '-'}
                                        </TableCell>
                                        <TableCell sx={{ fontWeight: 500 }}>
                                            {assignment.mentor_name || 'N/A'}
                                        </TableCell>
                                        <TableCell>
                                            {assignment.practicum_type ? (
                                                <Chip
                                                    label={assignment.practicum_type}
                                                    size="small"
                                                    sx={{ bgcolor: '#e0f2fe', color: '#0369a1', fontWeight: 600 }}
                                                />
                                            ) : (
                                                <Typography variant="body2" sx={{ color: '#9ca3af' }}>N/A</Typography>
                                            )}
                                        </TableCell>
                                        <TableCell>{assignment.subject || 'N/A'}</TableCell>
                                        <TableCell>{assignment.school_name || 'N/A'}</TableCell>
                                        <TableCell>
                                            {assignment.status === 'ok' ? (
                                                <CheckCircle sx={{ color: '#10b981' }} />
                                            ) : assignment.status === 'unallocated' ? (
                                                <Cancel sx={{ color: '#dc2626' }} />
                                            ) : (
                                                <Stack direction="row" spacing={1} alignItems="center">
                                                    <Warning sx={{ color: '#F59E0B' }} />
                                                    <Typography variant="caption" sx={{ color: '#d97706', fontWeight: 600 }}>
                                                        {assignment.issue || 'Problem'}
                                                    </Typography>
                                                </Stack>
                                            )}
                                        </TableCell>
                                        <TableCell align="right">
                                            <Button
                                                variant="secondary"
                                                size="small"
                                                onClick={() => handleManualAdjust(assignment.mentor_id)}
                                                startIcon={<EditIcon sx={{ fontSize: 16 }} />}
                                            >
                                                Anpassen
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                    {filteredAssignments.length > 0 && (
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', px: 2, py: 1, borderTop: '1px solid #e5e7eb' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                <Typography variant="body2" sx={{ color: '#6b7280' }}>
                                    {`${page * rowsPerPage + 1}-${Math.min((page + 1) * rowsPerPage, filteredAssignments.length)} von ${filteredAssignments.length}`}
                                </Typography>
                                {totalPages > 1 && (
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        <Typography variant="body2" sx={{ color: '#6b7280' }}>
                                            Gehe zu Seite:
                                        </Typography>
                                        <FormControl size="small" sx={{ minWidth: 80 }}>
                                            <Select
                                                value={page}
                                                onChange={handlePageJump}
                                                sx={{ 
                                                    height: 32,
                                                    fontSize: '0.875rem',
                                                    '& .MuiOutlinedInput-notchedOutline': {
                                                        borderColor: '#d1d5db'
                                                    }
                                                }}
                                            >
                                                {Array.from({ length: totalPages }, (_, i) => (
                                                    <MenuItem key={i} value={i}>
                                                        {i + 1}
                                                    </MenuItem>
                                                ))}
                                            </Select>
                                        </FormControl>
                                    </Box>
                                )}
                            </Box>
                            <TablePagination
                                component="div"
                                count={filteredAssignments.length}
                                page={page}
                                onPageChange={handleChangePage}
                                rowsPerPage={rowsPerPage}
                                rowsPerPageOptions={[25]}
                                labelDisplayedRows={() => ''}
                                sx={{ 
                                    border: 'none',
                                    '& .MuiTablePagination-toolbar': {
                                        minHeight: 'auto',
                                        padding: 0
                                    }
                                }}
                            />
                        </Box>
                    )}
                </TableContainer>
            )}

            {/* Navigation Footer */}
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', pt: 2 }}>
                <Button
                    onClick={onComplete}
                    size="large"
                    endIcon={<ArrowForward />}
                >
                    Abschließen & Berichte generieren
                </Button>
            </Box>

            {/* The Adjust Assignment Dialog */}
            <AdjustAssignmentDialog
                open={!!adjustingMentorId}
                mentorId={adjustingMentorId}
                onClose={() => setAdjustingMentorId(null)}
                onSaveSuccess={(updatedAssignments) => {
                    setAdjustingMentorId(null);
                    fetchAssignments(); 
                }}
            />

            {/* Reset Confirmation Dialog */}
            <Dialog 
                open={resetDialogOpen} 
                onClose={handleResetCancel}
                maxWidth="sm"
                fullWidth
            >
                <DialogTitle sx={{ fontWeight: 700, color: '#dc2626' }}>
                    Alle Zuweisungen zurücksetzen?
                </DialogTitle>
                <DialogContent dividers>
                    <Alert severity="warning" sx={{ mb: 2 }}>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            Diese Aktion kann nicht rückgängig gemacht werden!
                        </Typography>
                    </Alert>
                    <Typography variant="body2" sx={{ color: '#4b5563' }}>
                        Alle Assignment-Datensätze werden dauerhaft aus der Datenbank gelöscht. 
                        Dies umfasst Zuweisungen aus allen akademischen Jahren.
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#4b5563', mt: 2 }}>
                        Möchten Sie fortfahren?
                    </Typography>
                </DialogContent>
                <DialogActions sx={{ px: 3, py: 2 }}>
                    <Button 
                        onClick={handleResetCancel} 
                        variant="secondary"
                        disabled={resetting}
                    >
                        Abbrechen
                    </Button>
                    <Button 
                        onClick={handleResetConfirm}
                        disabled={resetting}
                        sx={{ 
                            bgcolor: '#dc2626',
                            color: 'white',
                            '&:hover': { bgcolor: '#b91c1c' }
                        }}
                    >
                        {resetting ? 'Wird zurückgesetzt...' : 'Ja, alle löschen'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default AllocationResultsStep;