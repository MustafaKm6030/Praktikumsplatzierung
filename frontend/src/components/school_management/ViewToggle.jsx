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