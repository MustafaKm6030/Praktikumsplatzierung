import React from 'react';
import { Stack } from '@mui/material';
import {
  PersonAdd as AddIcon,
  FileUpload as UploadIcon,
  FileDownload as DownloadIcon,
} from '@mui/icons-material';
import Button from '../ui/Button';

const TeachersActionButtons = ({ onAddTeacher, onImport, onExport }) => {
  return (
    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 3 }}>
      <Button
        startIcon={<AddIcon />}
        onClick={onAddTeacher}
        variant="primary"
        size="medium"
      >
        Neue Praktikumslehrkraft hinzufügen
      </Button>

      <Button
        startIcon={<UploadIcon />}
        onClick={onImport}
        variant="primary"
        size="medium"
      >
        Praktikumslehrkräfte importieren (CSV/Excel)
      </Button>

      <Button
        startIcon={<DownloadIcon />}
        onClick={onExport}
        variant="primary"
        size="medium"
      >
        Praktikumslehrkräfte exportieren
      </Button>
    </Stack>
  );
};

export default TeachersActionButtons;
