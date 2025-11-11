import React from 'react';
import { Button, Stack } from '@mui/material';
import {
    Add as AddIcon,
    FileUpload as UploadIcon,
    FileDownload as DownloadIcon,
} from '@mui/icons-material';

/**
 * Action Buttons Component
 * @param {Object} props
 * @param {function} props.onAddSchool - Handler for add school
 * @param {function} props.onImport - Handler for import
 * @param {function} props.onExport - Handler for export
 */
const ActionButtons = ({ onAddSchool, onImport, onExport }) => {
    return (
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 3 }}>
            <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={onAddSchool}
                sx={{ backgroundColor: '#000', '&:hover': { backgroundColor: '#333' } }}
            >
                Add New School
            </Button>
            <Button
                variant="outlined"
                startIcon={<UploadIcon />}
                onClick={onImport}
            >
                Import Schools (CSV/Excel)
            </Button>
            <Button
                variant="outlined"
                startIcon={<DownloadIcon />}
                onClick={onExport}
            >
                Export School List
            </Button>
        </Stack>
    );
};

export default ActionButtons;