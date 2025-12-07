import React from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import WidgetContainer from './WidgetContainer';

/**
 * Widget 1: Praktika Status Overview
 * Shows assignment status for each praktikum type
 */
const PraktikaStatusWidget = ({ data = [] }) => {
    return (
        <WidgetContainer >
            <TableContainer>
                <Table>
                    <TableHead>
                        <TableRow sx={{ backgroundColor: '#fef9f3' }}>
                            <TableCell><strong>Praktikum</strong></TableCell>
                            <TableCell align="center"><strong>Bedarf</strong></TableCell>
                            <TableCell align="center"><strong>Zugewiesen</strong></TableCell>
                            <TableCell align="center"><strong>Nicht zugewiesen</strong></TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {data.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={4} align="center" sx={{ py: 4, color: '#6b7280' }}>
                                    Keine Zuteilungsdaten verfügbar
                                </TableCell>
                            </TableRow>
                        ) : (
                            data.map((item, index) => (
                                <TableRow key={index} sx={{ '&:hover': { backgroundColor: '#f9f9f9' } }}>
                                    <TableCell sx={{ fontWeight: 600 }}>{item.practicum_type}</TableCell>
                                    <TableCell align="center">{item.demand_slots}</TableCell>
                                    <TableCell align="center" sx={{ color: '#10b981', fontWeight: 600 }}>
                                        {item.assigned_slots}
                                    </TableCell>
                                    <TableCell align="center" sx={{
                                        color: item.unassigned_slots > 0 ? '#dc2626' : '#6b7280',
                                        fontWeight: item.unassigned_slots > 0 ? 600 : 400
                                    }}>
                                        {item.unassigned_slots}
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </TableContainer>
        </WidgetContainer>
    );
};

export default PraktikaStatusWidget;