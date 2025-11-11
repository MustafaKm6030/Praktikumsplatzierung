import React from 'react';
import { FormControl, InputLabel, Select, MenuItem } from '@mui/material';

/**
 * Reusable Filter Select Component
 * @param {Object} props
 * @param {string} props.label - Label for the select
 * @param {string} props.value - Current selected value
 * @param {function} props.onChange - Change handler
 * @param {string[]} props.options - Array of options to display
 * @param {boolean} [props.disabled] - Whether the select is disabled
 * @param {number} [props.minWidth] - Minimum width in pixels
 */
const FilterSelect = ({
                          label,
                          value,
                          onChange,
                          options,
                          disabled = false,
                          minWidth = 150
                      }) => {
    return (
        <FormControl sx={{ minWidth }} disabled={disabled}>
            <InputLabel>{label}</InputLabel>
            <Select
                value={value}
                label={label}
                variant="outlined"
                onChange={onChange}
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