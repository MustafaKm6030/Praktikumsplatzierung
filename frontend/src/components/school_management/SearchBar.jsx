import React from 'react';
import { Search as SearchIcon } from '@mui/icons-material';
import TextField from '../utils/TextField';

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
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            startIcon={<SearchIcon sx={{ color: '#6b7280' }} />}
            fullWidth
        />
    );
};

export default SearchBar;