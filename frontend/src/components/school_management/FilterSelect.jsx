import React from 'react';
import { FormControl, InputLabel, Select, MenuItem } from '@mui/material';

const FilterSelect = ({
                          label,
                          value,
                          onChange,
                          options,
                          disabled = false,
                          minWidth = 150
                      }) => {
    return (
        <FormControl
            sx={{
                minWidth,
                '& .MuiOutlinedInput-root': {
                    borderRadius: '10px',
                    backgroundColor: 'white',
                    '& fieldset': {
                        borderColor: '#FAB95A',
                        borderWidth: '2px',
                    },
                    '&:hover fieldset': {
                        borderColor: '#FAB95A',
                    },
                    '&.Mui-focused fieldset': {
                        borderColor: '#FAB95A',
                        borderWidth: '2px',
                    },
                },
                '& .MuiInputLabel-root': {
                    color: '#F8971C',
                    fontWeight: 500,
                    '&.Mui-focused': {
                        color: '#F8971C',
                    },
                },
                '& .MuiSelect-icon': {
                    color: '#F8971C',
                },
            }}
            disabled={disabled}
        >
            <InputLabel>{label}</InputLabel>
            <Select
                value={value}
                label={label}
                variant="outlined"
                onChange={onChange}
                sx={{
                    '& .MuiSelect-select': {
                        color: '#333',
                        fontWeight: 500,
                    },
                }}
                MenuProps={{
                    PaperProps: {
                        sx: {
                            borderRadius: '10px',
                            marginTop: '4px',
                            boxShadow: '0 4px 12px rgba(248, 151, 28, 0.15)',
                            '& .MuiMenuItem-root': {
                                '&:hover': {
                                    backgroundColor: 'rgba(248, 151, 28, 0.1)',
                                },
                                '&.Mui-selected': {
                                    backgroundColor: 'rgba(248, 151, 28, 0.2)',
                                    '&:hover': {
                                        backgroundColor: 'rgba(248, 151, 28, 0.25)',
                                    },
                                },
                            },
                        },
                    },
                }}
            >
                <MenuItem value="all">All {label}s</MenuItem>
                {options.map(option => (
                    <MenuItem key={option} value={option}>
                        {option}
                    </MenuItem>
                ))}
            </Select>
        </FormControl>
    );
};

export default FilterSelect;