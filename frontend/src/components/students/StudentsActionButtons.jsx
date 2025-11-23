import React from 'react';
import { Stack } from '@mui/material';
import {
  PersonAdd as AddIcon,
  FileUpload as UploadIcon,
  FileDownload as DownloadIcon,
} from '@mui/icons-material';
import Button from '../ui/Button';

const StudentsActionButtons = ({ onAddStudent, onImport, onExport }) => {
  return (
    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 3 }}>
      <Button
        startIcon={<AddIcon />}
        onClick={onAddStudent}
        variant="primary"
        size="medium"
      >
        Add New Student
      </Button>

      <Button
        startIcon={<UploadIcon />}
        onClick={onImport}
        variant="primary"
        size="medium"
      >
        Import Students (CSV/Excel)
      </Button>

      <Button
        startIcon={<DownloadIcon />}
        onClick={onExport}
        variant="primary"
        size="medium"
      >
        Export Student List mohamed
      </Button>
    </Stack>
  );
};

export default StudentsActionButtons;
