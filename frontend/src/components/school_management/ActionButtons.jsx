import React from 'react';
import { Button, Stack } from '@mui/material';
import {
    Add as AddIcon,
    FileUpload as UploadIcon,
    FileDownload as DownloadIcon,
} from '@mui/icons-material';

const ActionButtons = ({ onAddSchool, onImport, onExport }) => {
    const primaryButtonStyle = {
       background: 'linear-gradient(135deg, #F8971C 0%, #fbbd61 100%);',
        borderRadius: '12px',
        color: '#2d2f38',
        borderColor: '#F8971C',
        border: 'none',
        textTransform: 'none',
        padding: '10px 24px',
        fontWeight: 600,
        fontFamily: 'Apple Braille',

    '&:hover': {
            background:'linear-gradient(135deg, #F8971C 0%, #fbbd61 100%);',
            transform: 'translateY(-1px)',
            color: 'white',

        }
    };



    return (
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 3 }}>
            <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={onAddSchool}
                sx={primaryButtonStyle}
            >
                Add New School
            </Button>
            <Button
                variant="contained"
                startIcon={<UploadIcon />}
                onClick={onImport}
                sx={primaryButtonStyle}
            >
                Import Schools (CSV/Excel)
            </Button>
            <Button
                variant="contained"
                startIcon={<DownloadIcon />}
                onClick={onExport}
                sx={primaryButtonStyle}
            >
                Export School List
            </Button>
        </Stack>
    );
};

export default ActionButtons;