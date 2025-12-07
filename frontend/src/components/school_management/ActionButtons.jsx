import React from 'react';
import { Stack } from '@mui/material';
import {
    Add as AddIcon,
    FileUpload as UploadIcon,
    FileDownload as DownloadIcon,
} from '@mui/icons-material';
import Button from '../ui/Button';

const ActionButtons = ({ onAddSchool, onImport, onExport }) => {
    return (
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 3 }}>
            <Button
                startIcon={<AddIcon />}
                onClick={onAddSchool}
                variant="primary"
                size="medium"
            >
                Neue Schule hinzufügen
            </Button>
            <Button
                startIcon={<UploadIcon />}
                onClick={onImport}
                variant="primary"
                size="medium"
            >
                Schulen importieren (CSV/Excel)
            </Button>
            <Button
                startIcon={<DownloadIcon />}
                onClick={onExport}
                variant="primary"
                size="medium"
            >
                Schulliste exportieren
            </Button>
        </Stack>
    );
};

export default ActionButtons;