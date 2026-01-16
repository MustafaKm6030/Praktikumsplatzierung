import React from 'react';
import { Stack, CircularProgress } from '@mui/material';
import {
    Add as AddIcon,
    FileUpload as UploadIcon,
    FileDownload as DownloadIcon,
    TravelExplore as GeocodeIcon,
} from '@mui/icons-material';
import Button from '../ui/Button';

const ActionButtons = ({ onAddSchool, onImport, onExport, onGeocode, isGeocoding = false }) => {
    return (
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 3 }}>
            <Button
                startIcon={<AddIcon />}
                onClick={onAddSchool}
                variant="primary"
                size="medium"
                disabled={isGeocoding}
            >
                Neue Schule hinzufügen
            </Button>
            <Button
                startIcon={<UploadIcon />}
                onClick={onImport}
                variant="primary"
                size="medium"
                disabled={isGeocoding}
            >
                Schulen importieren (CSV/Excel)
            </Button>
            <Button
                startIcon={isGeocoding ? <CircularProgress size={20} color="inherit" /> : <GeocodeIcon />}
                onClick={onGeocode}
                variant="secondary"
                size="medium"
                disabled={isGeocoding}
            >
                {isGeocoding ? 'Koordinaten werden gefunden...' : 'Fehlende Koordinaten finden'}
            </Button>
            <Button
                startIcon={<DownloadIcon />}
                onClick={onExport}
                variant="primary"
                size="medium"
                disabled={isGeocoding}
            >
                Schulliste exportieren
            </Button>
        </Stack>
    );
};

export default ActionButtons;