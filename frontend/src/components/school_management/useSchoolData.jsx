import { useState, useEffect, useCallback, useMemo } from 'react';

/**
 * @typedef {Object} School
 * @property {number} id
 * @property {string} name
 * @property {string} district
 * @property {string} school_type
 * @property {string} city
 * @property {number} zone
 * @property {string} opnv_code
 * @property {number} distance_km 
 * @property {boolean} is_active
 * @property {number | null} latitude 
 * @property {number | null} longitude 
 */

/**
 * Custom hook for managing school data.
 * This hook is the single source of truth for fetching, filtering,
 * and providing school data to the UI.
 */
const useSchoolData = () => {
    /** @type {[School[], React.Dispatch<React.SetStateAction<School[]>>]} */
    const [schools, setSchools] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // --- State for user's filter selections ---
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedDistrict, setSelectedDistrict] = useState('all');
    const [selectedType, setSelectedType] = useState('all');
    const [selectedZone, setSelectedZone] = useState('all');

    // Fetch schools from API
    const fetchSchools = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch('/api/schools/'); // Correct endpoint
            if (!response.ok) {
                // Log error for debugging but don't show to user
                console.error('Failed to fetch schools:', response.status, response.statusText);

                // For development: show more details
                if (process.env.NODE_ENV === 'development') {
                    console.error('Response details:', {
                        status: response.status,
                        statusText: response.statusText,
                        url: response.url
                    });
                }
                throw new Error('Failed to fetch');
            }

            const data = await response.json();
            setSchools(data);

        } catch (err) {
            console.error('Error fetching schools:', err);

            // For development: show full error
            if (process.env.NODE_ENV === 'development') {
                console.error('Full error details:', {
                    message: err instanceof Error ? err.message : 'Unknown error',
                    stack: err instanceof Error ? err.stack : undefined
                });
            }
            // Fallback to avoid crash
            setSchools([]);
        } finally {
            setLoading(false);
        }
    }, [setError]);

    // Initial data fetch on component mount
    useEffect(() => {
        void fetchSchools();
    }, [fetchSchools]);

    // --- DERIVED STATE using useMemo for efficiency ---

    // 1. Unique filter options are derived from the master 'schools' list.
    // This recalculates ONLY when the 'schools' array changes.
    const { districts, types, zones } = useMemo(() => {
        const uniqueDistricts = [...new Set(schools.map(s => s.district).filter(Boolean))].sort();
        const uniqueTypes = [...new Set(schools.map(s => s.school_type).filter(Boolean))].sort();
        const uniqueZones = [...new Set(schools.map(s => s.zone).filter(Boolean))].sort((a, b) => a - b);

        return { districts: uniqueDistricts, types: uniqueTypes, zones: uniqueZones };
    }, [schools]);

    // 2. The list of filtered schools is derived from the master 'schools' list and the current filter states.
    // This recalculates ONLY when schools or any filter value changes.
    const filteredSchools = useMemo(() => {
        return schools.filter(school => {
            // Search Query Filter
            const matchesSearch = !searchQuery ||
                school.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                school.district?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                school.city?.toLowerCase().includes(searchQuery.toLowerCase());

            // Dropdown Filters
            const matchesDistrict = selectedDistrict === 'all' || school.district === selectedDistrict;
            const matchesType = selectedType === 'all' || school.school_type === selectedType;
            const matchesZone = selectedZone === 'all' || school.zone === parseInt(selectedZone, 10);

            return matchesSearch && matchesDistrict && matchesType && matchesZone;
        });
    }, [searchQuery, selectedDistrict, selectedType, selectedZone, schools]);

    return {
        // Master data and status
        schools,
        loading,
        error,
        fetchSchools, // Expose refetch function

        // Filtered data for display
        filteredSchools,

        // State and setters for filter controls
        searchQuery,
        setSearchQuery,
        selectedDistrict,
        setSelectedDistrict,
        selectedType,
        setSelectedType,
        selectedZone,
        setSelectedZone,

        // Derived options for filter dropdowns
        districts,
        types,
        zones,
    };
};

export default useSchoolData;