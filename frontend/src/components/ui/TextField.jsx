import React from 'react';
import { TextField as MuiTextField, InputAdornment } from '@mui/material';

/**
 * Reusable TextField Component
 * @param {Object} props
 * @param {string} [props.label] - Input label
 * @param {string} [props.value] - Input value
 * @param {function} [props.onChange] - Change handler
 * @param {string} [props.placeholder] - Placeholder text
 * @param {'text' | 'email' | 'password' | 'number' | 'date' | 'tel' | 'url'} [props.type='text'] - Input type
 * @param {boolean} [props.required=false] - Required field
 * @param {boolean} [props.disabled=false] - Disabled state
 * @param {boolean} [props.fullWidth=true] - Full width input
 * @param {boolean} [props.multiline=false] - Multiline input (textarea)
 * @param {number} [props.rows] - Number of rows for multiline
 * @param {React.ReactNode} [props.startIcon] - Icon at the start
 * @param {React.ReactNode} [props.endIcon] - Icon at the end
 * @param {string} [props.helperText] - Helper text below input
 * @param {boolean} [props.error=false] - Error state
 * @param {Object} [props.sx] - Additional MUI sx styles
 * @param {string} [props.id] - Input ID
 * @param {string} [props.name] - Input name
 * @param {number | string} [props.step] - Step for number inputs
 */
const TextField = ({
                       label,
                       value,
                       onChange,
                       placeholder,
                       type = 'text',
                       required = false,
                       disabled = false,
                       fullWidth = true,
                       multiline = false,
                       rows,
                       startIcon,
                       endIcon,
                       helperText,
                       error = false,
                       sx = {},
                       id,
                       name,
                       step,
                       ...rest
                   }) => {
    const textFieldStyle = {
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
            '& input, & textarea': {
                color: '#333',
                fontWeight: 500,
                '&::placeholder': {
                    color: '#9ca3af',
                    opacity: 0.8,
                },
            },
        },
        '& .MuiInputLabel-root': {
            color: error ? '#dc2626' : '#6b7280',
            fontWeight: 500,
            '&.Mui-focused': {
                color: error ? '#dc2626' : '#F8971C',
            },
        },
        '& .MuiFormHelperText-root': {
            marginLeft: '4px',
            fontSize: '12px',
            color: error ? '#dc2626' : '#6b7280',
        },
        ...sx,
    };

    const InputProps = {};

    if (startIcon) {
        InputProps.startAdornment = (
            <InputAdornment position="start">
                {startIcon}
            </InputAdornment>
        );
    }

    if (endIcon) {
        InputProps.endAdornment = (
            <InputAdornment position="end">
                {endIcon}
            </InputAdornment>
        );
    }

    return (
        <MuiTextField
            id={id}
            name={name}
            label={label}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            type={type}
            required={required}
            disabled={disabled}
            fullWidth={fullWidth}
            multiline={multiline}
            rows={rows}
            helperText={helperText}
            error={error}
            variant="outlined"
            InputProps={InputProps}
            sx={textFieldStyle}
            inputProps={step ? { step } : {}}
            {...rest}
        />
    );
};

export default TextField;