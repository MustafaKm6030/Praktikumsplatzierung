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

/**
 * School Table Component
 * @param {Object} props
 * @param {Array} props.schools - Array of school objects
 * @param {function} [props.onView] - Handler for view action
 * @param {function} [props.onEdit] - Handler for edit action
 * @param {function} [props.onDelete] - Handler for delete action
 */
const SchoolTable = ({ schools, onView, onEdit, onDelete }) => {
    return (
        <TableContainer component={Paper}>
            <Table>
                <TableHead>
                    <TableRow sx={{ backgroundColor: '#f8f8f8' }}>
                        <TableCell><strong>School Name</strong></TableCell>
                        <TableCell><strong>District</strong></TableCell>
                        <TableCell><strong>Type</strong></TableCell>
                        <TableCell><strong>City</strong></TableCell>
                        <TableCell><strong>Zone</strong></TableCell>
                        <TableCell><strong>Capacity</strong></TableCell>
                        <TableCell><strong>Status</strong></TableCell>
                        <TableCell align="center"><strong>Actions</strong></TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {schools.length === 0 ? (
                        <TableRow>
                            <TableCell colSpan={8} align="center" sx={{ py: 8, color: 'text.secondary' }}>
                                No schools found matching your criteria
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