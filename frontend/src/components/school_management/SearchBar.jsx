import React from 'react';
import { TextField, InputAdornment } from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';

/**
 * Search Bar Component
 * @param {Object} props
 * @param {string} props.value - Current search value
 * @param {function} props.onChange - Change handler
 * @param {string} [props.placeholder] - Placeholder text
 */
const SearchBar = ({ value, onChange, placeholder = 'Search...' }) => {
    return (
        <TextField
            fullWidth
            placeholder={placeholder}
            value={value}
            onChange={onChange}
            InputProps={{
                startAdornment: (
                    <InputAdornment position="start">
                        <SearchIcon />
                    </InputAdornment>
                ),
            }}
            sx={{ flex: 1 }}
        />
    );
};

export default SearchBar;