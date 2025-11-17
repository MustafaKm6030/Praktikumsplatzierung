import React from 'react';
import { TableCell, TableRow, IconButton, Chip } from '@mui/material';
import {
    Visibility as VisibilityIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
} from '@mui/icons-material';

/**
 * Get status color for Chip component
 * @param {string | undefined} status
 * @returns {'success' | 'error' | 'warning' | 'default'}
 */
const getStatusColor = (status) => {
    const statusLower = status?.toLowerCase();
    if (statusLower === 'active') return 'success';
    if (statusLower === 'inactive') return 'error';
    if (statusLower === 'pending') return 'warning';
    return 'default';
};

/**
 * School Table Row Component
 * @param {Object} props
 * @param {Object} props.school - School object
 * @param {function} [props.onView] - Handler for view action
 * @param {function} [props.onEdit] - Handler for edit action
 * @param {function} [props.onDelete] - Handler for delete action
 */
const SchoolTableRow = ({ school, onView, onEdit, onDelete }) => {
    return (
        <TableRow sx={{ '&:hover': { backgroundColor: '#f9f9f9' } }}>
            <TableCell sx={{ fontWeight: 500 }}>{school.name || 'N/A'}</TableCell>
            <TableCell>{school.district || 'N/A'}</TableCell>
            <TableCell>{school.type || 'N/A'}</TableCell>
            <TableCell>{school.city || 'N/A'}</TableCell>
            <TableCell>{school.zone || 'N/A'}</TableCell>
            <TableCell>{school.capacity || 'N/A'}</TableCell>
            <TableCell>
                <Chip
                    label={school.status || 'Active'}
                    color={getStatusColor(school.status)}
                    size="small"
                />
            </TableCell>
            <TableCell align="center">
                <IconButton
                    size="small"
                    color="primary"
                    title="View Details"
                    onClick={() => onView && onView(school)}
                >
                    <VisibilityIcon fontSize="small" />
                </IconButton>
                <IconButton
                    size="small"
                    color="primary"
                    title="Edit"
                    onClick={() => onEdit && onEdit(school)}
                >
                    <EditIcon fontSize="small" />
                </IconButton>
                <IconButton
                    size="small"
                    color="error"
                    title="Delete"
                    onClick={() => onDelete && onDelete(school)}
                >
                    <DeleteIcon fontSize="small" />
                </IconButton>
            </TableCell>
        </TableRow>
    );
};

export default SchoolTableRow;