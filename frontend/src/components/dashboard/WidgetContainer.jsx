import React from 'react';
import { Paper, Typography, Box } from '@mui/material';

/**
 * Reusable Widget Container Component
 * @param {string} title - Widget title
 * @param {React.ReactNode} children - Widget content
 * @param {React.ReactNode} [action] - Optional action button in header
 * @param {Object} [sx] - Additional MUI sx styles
 */
const WidgetContainer = ({ title, children, action, sx = {} }) => {
    return (
        <Paper
            sx={{
                p: 2,
                borderRadius: '30px',  // Match layout-content border radius
                backgroundColor: 'white',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',  // Match layout-content shadow
                border: 'none',  // Remove border to match layout-content
                ...sx,
            }}
        >
            {title && (
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" sx={{ fontWeight: 700, color: '#1f2937', fontSize: '16px' }}>
                        {title}
                    </Typography>
                    {action && <Box>{action}</Box>}
                </Box>
            )}
            {children}
        </Paper>
    );
};

export default WidgetContainer;