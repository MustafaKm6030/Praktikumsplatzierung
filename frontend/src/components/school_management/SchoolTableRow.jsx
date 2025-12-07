import React from 'react';
import { TableCell, TableRow, IconButton, Chip } from '@mui/material';
import {
    Visibility as VisibilityIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
} from '@mui/icons-material';

/**
 * Get status color for Chip component
 * @param {boolean | undefined} isActive
 * @returns {'success' | 'error' | 'warning' | 'default'}
 */
const getStatusColor = (isActive) => {
    if (isActive === false) return 'error';
    if (isActive === true) return 'success';
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
    const isActive = school.is_active;
    return (
        <TableRow sx={{ '&:hover': { backgroundColor: '#f9f9f9' } }}>
            <TableCell sx={{ fontWeight: 500 }}>{school.name || 'N/A'}</TableCell>
            <TableCell>{school.district || 'N/A'}</TableCell>
            <TableCell>{school.school_type || 'N/A'}</TableCell>
            <TableCell>{school.city || 'N/A'}</TableCell>
            <TableCell>{school.zone || 'N/A'}</TableCell>
            <TableCell>{school.opnv_code || 'N/A'}</TableCell>
            <TableCell>{school.distance_km || 'N/A'}</TableCell>
            <TableCell>
                <Chip
                    label={isActive ? 'Aktiv' : 'Inaktiv'}
                    color={getStatusColor(isActive)}
                    size="small"
                />
            </TableCell>
            <TableCell align="center">
                <IconButton
                    size="small"
                    color="primary"
                    title="Details anzeigen"
                    onClick={() => onView && onView(school)}
                >
                    <VisibilityIcon fontSize="small" />
                </IconButton>
                <IconButton
                    size="small"
                    color="primary"
                    title="Bearbeiten"
                    onClick={() => onEdit && onEdit(school)}
                >
                    <EditIcon fontSize="small" />
                </IconButton>
                <IconButton
                    size="small"
                    color="error"
                    title="Löschen"
                    onClick={() => onDelete && onDelete(school)}
                >
                    <DeleteIcon fontSize="small" />
                </IconButton>
            </TableCell>
        </TableRow>
    );
};

export default SchoolTableRow;