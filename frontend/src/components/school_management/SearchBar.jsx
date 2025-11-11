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
                        <SearchIcon sx={{ color: '#F8971C' }} />
                    </InputAdornment>
                ),
            }}
            sx={{
                flex: 1,
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
                    '& input': {
                        color: '#333',
                        fontWeight: 500,
                        '&::placeholder': {
                            color: '#F8971C',
                            opacity: 0.7,
                        },
                    },
                },
                '& .MuiInputLabel-root': {
                    color: '#F8971C',
                    fontWeight: 500,
                    '&.Mui-focused': {
                        color: '#F8971C',
                    },
                },
            }}
        />
    );
};

export default SearchBar;