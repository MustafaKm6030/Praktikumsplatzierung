import React from 'react';
import {
    TableContainer,
    Table,
    TableHead,
    TableBody,
    TableRow,
    TableCell,
    Paper,
} from '@mui/material';
import SchoolTableRow from './SchoolTableRow';

const SchoolTable = ({ schools, onView, onEdit, onDelete }) => {
    return (
        <TableContainer component={Paper} sx={{
            borderRadius: '12px',
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.08)',
            backgroundColor: 'white'
        }}>
            <Table>
                <TableHead>
                    <TableRow sx={{ backgroundColor: '#fef9f3' }}>
                        <TableCell><strong>Schulname</strong></TableCell>
                        <TableCell><strong>Bezirk</strong></TableCell>
                        <TableCell><strong>Schultyp</strong></TableCell>
                        <TableCell><strong>Stadt</strong></TableCell>
                        <TableCell><strong>Zone</strong></TableCell>
                        <TableCell><strong>ÖPNV Code</strong></TableCell>
                        <TableCell><strong>Entfernung (km)</strong></TableCell>
                        <TableCell><strong>Hat Koordinaten</strong></TableCell>
                        <TableCell><strong>Status</strong></TableCell>
                        <TableCell align="center"><strong>Aktionen</strong></TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {schools.length === 0 ? (
                        <TableRow>
                            <TableCell colSpan={10} align="center" sx={{ py: 8, color: 'text.secondary' }}>
                                Keine Schulen gefunden, die Ihren Kriterien entsprechen
                            </TableCell>
                        </TableRow>
                    ) : (
                        schools.map((school) => (
                            <SchoolTableRow
                                key={school.id}
                                school={school}
                                onView={onView}
                                onEdit={onEdit}
                                onDelete={onDelete}
                            />
                        ))
                    )}
                </TableBody>
            </Table>
        </TableContainer>
    );
};

export default SchoolTable;