import React from 'react';
import { Box, Typography } from '@mui/material';

/**
 * KPI Card Component
 * @param {string} label - KPI label
 * @param {string|number} value - KPI value
 * @param {ReactNode} [icon] - Optional icon
 * @param {string} [color] - Accent color
 */
const KPICard = ({ label, value, icon, color = '#F8971C' }) => {
    return (
        <Box
            sx={{
                p: 2.5,
                borderRadius: '12px',
                border: '1px solid #e5e7eb',
                backgroundColor: 'white',
                display: 'flex',
                flexDirection: 'column',
                gap: 1,
            }}
        >
            {icon && (
                <Box
                    sx={{
                        width: 40,
                        height: 40,
                        borderRadius: '10px',
                        background: `linear-gradient(135deg, ${color}20 0%, ${color}10 100%)`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: color,
                        mb: 1,
                    }}
                >
                    {icon}
                </Box>
            )}
            <Typography variant="body2" sx={{ color: '#6b7280', fontSize: '13px', fontWeight: 500 }}>
                {label}
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 700, color: '#1f2937', fontSize: '28px' }}>
                {value}
            </Typography>
        </Box>
    );
};

export default KPICard;