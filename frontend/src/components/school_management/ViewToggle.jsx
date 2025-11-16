// ViewToggle.jsx
import React from 'react';
import MapIcon from '@mui/icons-material/Map';
import ListIcon from '@mui/icons-material/List';

import ButtonGroup from '../utils/ButtonGroup';

const ViewToggle = ({ viewMode, onViewChange }) => {
    const options = [
        { value: 'map', label: 'Map View', icon: <MapIcon /> },
        { value: 'list', label: 'List View', icon: <ListIcon /> }
    ];

    return (
        <ButtonGroup
            value={viewMode}
            onChange={onViewChange}
            options={options}
            size="medium"
        />
    );
};

export default ViewToggle;
