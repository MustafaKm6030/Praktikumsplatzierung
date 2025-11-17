import React, { useState, useEffect } from 'react';
import Loader from '../utils/Loader';

/**
 * Map View Component
 * Shows loader while simulating map load
 */
const MapView = () => {
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        setIsLoading(true);
    }, []);

    if (isLoading) {
        return <Loader message="Loading map..." />;
    }

    // After loading, show map placeholder
    return (
        <div style={{
            width: '100%',
            height: '600px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: '8px'
        }}>
        </div>
    );
};

export default MapView;