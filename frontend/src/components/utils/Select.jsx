import React from 'react';
import { FormControl, InputLabel, Select as MuiSelect, MenuItem } from '@mui/material';

/**
 * Reusable Select Component
 * @param {Object} props
 * @param {string} props.label - Select label
 * @param {string | number} props.value - Selected value
 * @param {function} props.onChange - Change handler
 * @param {Array<{value: string | number, label: string}>} props.options - Select options
 * @param {boolean} [props.showAllOption=true] - Show "All {label}s" option
 * @param {boolean} [props.required=false] - Required field
 * @param {boolean} [props.disabled=false] - Disabled state
 * @param {boolean} [props.fullWidth=true] - Full width select
 * @param {number | string} [props.minWidth=150] - Minimum width
 * @param {boolean} [props.error=false] - Error state
 * @param {string} [props.helperText] - Helper text below select
 * @param {Object} [props.sx] - Additional MUI sx styles
 * @param {string} [props.id] - Select ID
 * @param {string} [props.name] - Select name
 */
const Select = ({
                    label,
                    value,
                    onChange,
                    options = [],
                    showAllOption = true,
                    required = false,
                    disabled = false,
                    fullWidth = true,
                    minWidth = 150,
                    error = false,
                    helperText,
                    sx = {},
                    id,
                    name,
                    ...rest
                }) => {
    const formControlStyle = {
        minWidth: fullWidth ? '100%' : minWidth,
        '& .MuiOutlinedInput-root': {
            borderRadius: '10px',
            backgroundColor: 'white',
            '& fieldset': {
                borderColor: error ? '#dc2626' : '#e5e7eb',
                borderWidth: '1px',
            },
            '&:hover fieldset': {
                borderColor: error ? '#b91c1c' : '#d1d5db',
            },
            '&.Mui-focused fieldset': {
                borderColor: error ? '#dc2626' : '#FAB95A',
                borderWidth: '2px',
            },
        },
        '& .MuiInputLabel-root': {
            color: error ? '#dc2626' : '#6b7280',
            fontWeight: 500,
            '&.Mui-focused': {
                color: error ? '#dc2626' : '#F8971C',
            },
        },
        '& .MuiSelect-icon': {
            color: '#6b7280',
            '&.Mui-focused': {
                color: '#F8971C',
            },
        },
        '& .MuiFormHelperText-root': {
            marginLeft: '4px',
            fontSize: '12px',
            color: error ? '#dc2626' : '#6b7280',
        },
        ...sx,
    };

    const selectStyle = {
        '& .MuiSelect-select': {
            color: '#333',
            fontWeight: 500,
        },
    };

    const menuProps = {
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
    };

    return (
        <FormControl
            sx={formControlStyle}
            disabled={disabled}
            required={required}
            error={error}
            fullWidth={fullWidth}
        >
            <InputLabel id={`${id || name || label}-label`}>{label}</InputLabel>
            <MuiSelect
                labelId={`${id || name || label}-label`}
                id={id}
                name={name}
                value={value}
                label={label}
                onChange={onChange}
                variant="outlined"
                sx={selectStyle}
                MenuProps={menuProps}
                {...rest}
            >
                {showAllOption && (
                    <MenuItem value="all">All {label}s</MenuItem>
                )}
                {options.map((option) => (
                    <MenuItem
                        key={typeof option === 'object' ? option.value : option}
                        value={typeof option === 'object' ? option.value : option}
                    >
                        {typeof option === 'object' ? option.label : option}
                    </MenuItem>
                ))}
            </MuiSelect>
            {helperText && (
                <span style={{
                    marginLeft: '14px',
                    marginTop: '4px',
                    fontSize: '12px',
                    color: error ? '#dc2626' : '#6b7280'
                }}>
                    {helperText}
                </span>
            )}
        </FormControl>
    );
};

export default Select;