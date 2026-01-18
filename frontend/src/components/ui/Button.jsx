import React from 'react';
import { Button as MuiButton } from '@mui/material';

/**
 * Reusable Button Component
 * @param {Object} props
 * @param {React.ReactNode} props.children - Button content
 * @param {function} [props.onClick] - Click handler
 * @param {React.ReactNode} [props.startIcon] - Icon to display before text
 * @param {React.ReactNode} [props.endIcon] - Icon to display after text
 * @param {'primary' | 'secondary' | 'error' | 'success' | 'default'} [props.variant='primary'] - Button variant
 * @param {'small' | 'medium' | 'large'} [props.size='medium'] - Button size
 * @param {boolean} [props.disabled=false] - Disabled state
 * @param {boolean} [props.fullWidth=false] - Full width button
 * @param {'button' | 'submit' | 'reset'} [props.type='button'] - Button type
 * @param {Object} [props.sx] - Additional MUI sx styles
 * @param {string} [props.className] - Additional CSS classes
 */

// Define styles OUTSIDE the component
const SIZE_CONFIG = {
    small: { padding: '6px 16px', fontSize: '13px' },
    medium: { padding: '10px 24px', fontSize: '15px' },
    large: { padding: '14px 32px', fontSize: '16px' },
};

// Variant configurations
const PRIMARY_STYLE = {
    background: 'linear-gradient(135deg, #F8971C 0%, #fbbd61 100%)',
    color: '#2d2f38',
    '&:hover': {
        background: 'linear-gradient(135deg, #e88716 0%, #f5a842 100%)',
        transform: 'translateY(-1px)',
        color: 'white',
    },
};

const SECONDARY_STYLE = {
    background: 'white',
    color: '#FAB95A',
    border: '2px solid #FAB95A',
    '&:hover': {
        background: 'rgba(248, 151, 28, 0.1)',
        borderColor: '#FAB95A',
    },
};

const VARIANT_STYLES = {
    primary: PRIMARY_STYLE,
    secondary: SECONDARY_STYLE,
    // Add Mappings for standard MUI names to prevent crashes
    contained: PRIMARY_STYLE, 
    outlined: SECONDARY_STYLE,
    
    error: {
        background: 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)',
        color: 'white',
        '&:hover': {
            background: 'linear-gradient(135deg, #b91c1c 0%, #dc2626 100%)',
            transform: 'translateY(-1px)',
        },
    },
    success: {
        background: 'linear-gradient(135deg, #059669 0%, #10b981 100%)',
        color: 'white',
        '&:hover': {
            background: 'linear-gradient(135deg, #047857 0%, #059669 100%)',
            transform: 'translateY(-1px)',
        },
    },
    default: {
        background: '#f3f4f6',
        color: '#374151',
        '&:hover': {
            background: '#e5e7eb',
            transform: 'translateY(-1px)',
        },
    },
};

const Button = ({
                    children,
                    onClick,
                    startIcon,
                    endIcon,
                    variant = 'primary',
                    size = 'medium',
                    disabled = false,
                    fullWidth = false,
                    type = 'button',
                    sx = {},
                    className = '',
                    ...rest
                }) => {

    // SAFE ACCESS: If variant doesn't exist, fall back to 'primary'
    const activeVariantStyle = VARIANT_STYLES[variant] || VARIANT_STYLES.primary;

    // Combine base styles with dynamic props
    const buttonStyle = {
        borderRadius: '12px',
        textTransform: 'none',
        fontWeight: 600,
        fontFamily: 'Apple Braille, sans-serif',
        border: 'none',
        transition: 'all 0.2s cubic-bezier(.4,0,.2,1)',
        transform: 'scale(1)',
        boxShadow: disabled ? 'none' : '0 2px 8px rgba(0, 0, 0, 0.12)',

        ...SIZE_CONFIG[size],
        ...activeVariantStyle,

        '&:hover': {
            transform: 'scale(1.03) translateY(-1px)',
            // Safety check for hover styles
            ...(activeVariantStyle['&:hover'] || {}),
        },

        '&:active': {
            transform: 'scale(0.97)',
            boxShadow: '0 1px 4px rgba(0,0,0,0.15)',
        },

        '&:focus-visible': {
            outline: '3px solid rgba(248,151,28,0.4)',
            outlineOffset: '3px',
        },

        '&:disabled': {
            background: '#9ca3af',
            color: '#d1d5db',
            cursor: 'not-allowed',
            transform: 'none',
            boxShadow: 'none',
        },
        ...sx,
    };


    return (
        <MuiButton
            variant="contained" // We force MUI to use contained so our custom backgrounds work
            onClick={onClick}
            startIcon={startIcon}
            endIcon={endIcon}
            disabled={disabled}
            fullWidth={fullWidth}
            type={type}
            className={className}
            sx={buttonStyle}
            {...rest}
        >
            {children}
        </MuiButton>
    );
};

export default Button;