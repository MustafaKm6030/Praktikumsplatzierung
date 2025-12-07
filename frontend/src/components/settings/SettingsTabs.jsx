import React from 'react';
import { Box, Stack, Chip, Typography } from '@mui/material';

const TABS = [
    { id: 'general', label: 'Allgemein', enabled: true },
    { id: 'users', label: 'Benutzer', enabled: true },
    { id: 'praktikum', label: 'Praktikum', enabled: true },
    { id: 'geography', label: 'Karte', enabled: true },
];

function SettingsTabs({ activeTab, onTabChange }) {
    return (
        <Box sx={{ borderBottom: '2px solid #e5e7eb', mb: 4, overflowX: 'auto' }}>
            <Stack direction="row" spacing={0}>
                {TABS.map((tab) => {
                    const isActive = activeTab === tab.id;
                    return (
                        <Box
                            key={tab.id}
                            onClick={() => tab.enabled && onTabChange(tab.id)}
                            sx={{
                                position: 'relative',
                                px: 3,
                                py: 1.5,
                                cursor: tab.enabled ? 'pointer' : 'not-allowed',
                                borderBottom: isActive ? '3px solid #F8971C' : '3px solid transparent',
                                marginBottom: '-2px',
                                transition: 'all 0.2s ease',
                                opacity: tab.enabled ? 1 : 0.6,
                                '&:hover': tab.enabled ? { backgroundColor: '#f9f9f9' } : {},
                                minWidth: 'fit-content',
                                whiteSpace: 'nowrap',
                                display: 'flex',
                                alignItems: 'center',
                                gap: 1
                            }}
                        >
                            <Typography
                                sx={{
                                    fontSize: '15px',
                                    fontWeight: isActive ? 600 : 500,
                                    color: isActive ? '#F8971C' : 'inherit',
                                    fontFamily: 'Apple Braille, sans-serif'
                                }}
                            >
                                {tab.label}
                            </Typography>

                            {!tab.enabled && (
                                <Chip
                                    label="Kommt bald"
                                    size="small"
                                    sx={{
                                        height: '20px',
                                        fontSize: '11px',
                                        fontWeight: 600,
                                        backgroundColor: '#fef3c7',
                                        color: '#92400e',
                                    }}
                                />
                            )}
                        </Box>
                    );
                })}
            </Stack>
        </Box>
    );
}

export default SettingsTabs;