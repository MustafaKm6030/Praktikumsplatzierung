import React from 'react';
import { Box } from '@mui/material';
import styled from 'styled-components';

const LoaderWrapper = styled.div`
    width: 40px;
    aspect-ratio: 1;
    position: relative;
    transform: rotate(45deg);

    &:before,
    &:after {
        content: "";
        position: absolute;
        inset: 0;
        border-radius: 50% 50% 0 50%;
        background: #e38d13;
        mask: radial-gradient(circle 10px at 50% 50%, transparent 94%, #000);
    }

    &:after {
        animation: l6 1s infinite;
        transform: perspective(300px) translateZ(0px);
    }

    &.loader-primary:before,
    &.loader-primary:after {
        background: #1976d2;
    }

    &.loader-dark:before,
    &.loader-dark:after {
        background: #000000;
    }

    &.loader-light:before,
    &.loader-light:after {
        background: #ffffff;
    }

    @keyframes l6 {
        to {
            transform: perspective(300px) translateZ(150px);
            opacity: 0;
        }
    }
`;


const Loader = ({ message = 'Loading...', variant = "default" }) => {
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
            <LoaderWrapper className={`loader-${variant}`} />

            {message && (
                <Box sx={{ color: 'text.secondary', fontSize: '14px', mt: 2 }}>
                    {message}
                </Box>
            )}
        </Box>
    );
};

export default Loader;
