// ViewToggle.jsx
import React from 'react';
import MapIcon from '@mui/icons-material/Map';
import ListIcon from '@mui/icons-material/List';

import ButtonGroup from '../ui/ButtonGroup';

// Defined outside component to prevent recreation on every render
const VIEW_OPTIONS = [
    { value: 'map', label: 'Map View', icon: <MapIcon /> },
    { value: 'list', label: 'List View', icon: <ListIcon /> }
];

const ViewToggle = ({ viewMode, onViewChange }) => {
    return (
        <ButtonGroup
            value={viewMode}
            onChange={onViewChange}
            options={VIEW_OPTIONS}
            size="medium"
        />
    );
};

export default ViewToggle;
