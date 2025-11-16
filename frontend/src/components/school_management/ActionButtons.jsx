import React from 'react';
import { Stack } from '@mui/material';
import {
    Add as AddIcon,
    FileUpload as UploadIcon,
    FileDownload as DownloadIcon,
} from '@mui/icons-material';
import Button from '../utils/Button';

const ActionButtons = ({ onAddSchool, onImport, onExport }) => {
    return (
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 3 }}>
            <Button
                startIcon={<AddIcon />}
                onClick={onAddSchool}
                variant="primary"
                size="medium"
            >
                Add New School
            </Button>
            <Button
                startIcon={<UploadIcon />}
                onClick={onImport}
                variant="primary"
                size="medium"
            >
                Import Schools (CSV/Excel)
            </Button>
            <Button
                startIcon={<DownloadIcon />}
                onClick={onExport}
                variant="primary"
                size="medium"
            >
                Export School List
            </Button>
        </Stack>
    );
};

export default ActionButtons;