import React from 'react';
import { Box } from '@mui/material';
import './Loader.css';

/**
 * Custom animated loader component
 * @param {Object} props
 * @param {string} [props.message] - Optional loading message
 */
const Loader = ({ message = 'Loading...' }) => {
    return (
        <Box
            sx={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                py: 8,
                gap: 2
            }}
        >
            <div className="loader"></div>
            {message && (
                <Box sx={{ color: 'text.secondary', fontSize: '14px', mt: 2 }}>
                    {message}
                </Box>
            )}
        </Box>
    );
};

export default Loader;