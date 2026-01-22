import React from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import WidgetContainer from './WidgetContainer';

/**
 * Widget 1: Student Summary Overview
 * Shows total students, assigned, and unassigned students
 */
const PraktikaStatusWidget = ({ data = {} }) => {
    const { total_students = 0, assigned_students = 0, unassigned_students = 0 } = data;
    
    return (
        <WidgetContainer >
            <TableContainer>
                <Table>
                    <TableHead>
                        <TableRow sx={{ backgroundColor: '#fef9f3' }}>
                            <TableCell align="center"><strong>Gesamt Studenten</strong></TableCell>
                            <TableCell align="center"><strong>Zugewiesen</strong></TableCell>
                            <TableCell align="center"><strong>Nicht zugewiesen</strong></TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        <TableRow sx={{ '&:hover': { backgroundColor: '#f9f9f9' } }}>
                            <TableCell align="center" sx={{ fontWeight: 600 }}>
                                {total_students}
                            </TableCell>
                            <TableCell align="center" sx={{ color: '#10b981', fontWeight: 600 }}>
                                {assigned_students}
                            </TableCell>
                            <TableCell align="center" sx={{
                                color: unassigned_students > 0 ? '#dc2626' : '#6b7280',
                                fontWeight: unassigned_students > 0 ? 600 : 400
                            }}>
                                {unassigned_students}
                            </TableCell>
                        </TableRow>
                    </TableBody>
                </Table>
            </TableContainer>
        </WidgetContainer>
    );
};

export default PraktikaStatusWidget;