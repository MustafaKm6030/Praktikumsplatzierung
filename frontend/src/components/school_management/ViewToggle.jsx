import React from 'react';
import { ToggleButtonGroup, ToggleButton } from '@mui/material';
import { Map as MapIcon, ViewList as ListIcon } from '@mui/icons-material';

const ViewToggle = ({ viewMode, onViewChange }) => {
    return (
        <ToggleButtonGroup
            value={viewMode}
            exclusive
            onChange={(e, newView) => {
                if (newView !== null) {
                    onViewChange(newView);
                }
            }}
            size="small"
            sx={{
                '& .MuiToggleButton-root': {
                    borderRadius: '8px',
                    margin: '0 4px',
                    border: '2px solid #F8971C',
                    color: '#F8971C',
                    backgroundColor: 'white',
                    '&.Mui-selected': {
                        background: 'linear-gradient(135deg, #F8971C 0%, #fbbd61 100%)',
                        color: 'white',
                        boxShadow: '0 0 12px rgba(248, 151, 28, 0.35)',
                        '&:hover': {
                            background: 'linear-gradient(135deg, #e88716 0%, #f5a842 100%)',
                        }
                    },
                    '&:hover': {
                        backgroundColor: 'rgba(248, 151, 28, 0.08)',
                    }
                }
            }}
        >
            <ToggleButton value="map">
                <MapIcon sx={{ mr: 1 }} />
                Map View
            </ToggleButton>
            <ToggleButton value="list">
                <ListIcon sx={{ mr: 1 }} />
                List View
            </ToggleButton>
        </ToggleButtonGroup>
    );
};

export default ViewToggle;