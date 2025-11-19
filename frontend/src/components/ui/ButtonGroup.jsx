import React from 'react';
import { Stack } from '@mui/material';
import Button from './Button';

/**
 * Button Group Component for toggle-style buttons
 * @param {Object} props
 * @param {string | number} props.value - Currently selected value
 * @param {function} props.onChange - Change handler (receives the selected value)
 * @param {Array<{value: string | number, label: string, icon?: ReactNode}>} props.options - Button options
 * @param {'small' | 'medium' | 'large'} [props.size='medium'] - Button size
 */
const ButtonGroup = ({ value, onChange, options = [], size = 'medium' }) => {
    return (
        <Stack direction="row" spacing={1}>
            {options.map((option) => {
                const isSelected = value === option.value;

                return (
                    <Button
                        key={option.value}
                        variant={isSelected ? 'primary' : 'secondary'}
                        onClick={() => onChange(option.value)}
                        startIcon={option.icon}
                        size={size}
                        sx={{
                            boxShadow: isSelected ? '0 2px 8px rgba(248, 151, 28, 0.25)' : 'none',
                        }}
                    >
                        {option.label}
                    </Button>
                );
            })}
        </Stack>
    );
};

export default ButtonGroup;