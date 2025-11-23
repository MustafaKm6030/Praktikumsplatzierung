import React from 'react';
import { Box } from '@mui/material';

// Define Keyframes in a style object for reuse
const loaderKeyframes = {
    '@keyframes l6': {
        to: {
            transform: 'perspective(300px) translateZ(150px)',
            opacity: 0,
        }
    }
};

const Loader = ({ message = 'Loading...', variant = "default" }) => {
    // Map variant to colors
    const colors = {
        default: '#e38d13',
        primary: '#1976d2',
        dark: '#000000',
        light: '#ffffff',
    };

    const activeColor = colors[variant] || colors.default;

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', py: 8, gap: 2 }}>
            <Box
                sx={{
                    width: '40px',
                    aspectRatio: '1',
                    position: 'relative',
                    transform: 'rotate(45deg)',
                    ...loaderKeyframes,
                    '&:before, &:after': {
                        content: '""',
                        position: 'absolute',
                        inset: 0,
                        borderRadius: '50% 50% 0 50%',
                        background: activeColor,
                        mask: 'radial-gradient(circle 10px at 50% 50%, transparent 94%, #000)',
                    },
                    '&:after': {
                        animation: 'l6 1s infinite',
                        transform: 'perspective(300px) translateZ(0px)',
                    },
                }}
            />
            {message && (
                <Box sx={{ color: 'text.secondary', fontSize: '14px', mt: 2 }}>
                    {message}
                </Box>
            )}
        </Box>
    );
};

export default Loader;