import { useState, useEffect, useCallback, useMemo } from 'react';

/**
 * @typedef {Object} School
 * @property {number} id
 * @property {string} name
 * @property {string} district
 * @property {string} type
 * @property {string} city
 * @property {string} zone
 * @property {number} capacity
 * @property {string} status
 */

/**
 * Custom hook for managing school data
 * @returns {Object} School management state and functions
 */
const useSchoolData = () => {
    /** @type {[School[], React.Dispatch<React.SetStateAction<School[]>>]} */
    const [schools, setSchools] = useState([]);
    const [loading, setLoading] = useState(false);

    // Filter states
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedDistrict, setSelectedDistrict] = useState('all');
    const [selectedType, setSelectedType] = useState('all');
    const [selectedZone, setSelectedZone] = useState('all');

    // Fetch schools from API
    const fetchSchools = useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/schools');
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
            // Log error for debugging
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
    }, []);

    // Initial fetch
    useEffect(() => {
        void fetchSchools();
    }, [fetchSchools]);

    // derived state: Unique Filter Options
    // We use useMemo so these don't recalculate unless 'schools' data changes
    const { districts, types, zones } = useMemo(() => {
        return {
            districts: [...new Set(schools.map(s => s.district).filter(Boolean))],
            types: [...new Set(schools.map(s => s.type).filter(Boolean))],
            zones: [...new Set(schools.map(s => s.zone).filter(Boolean))]
        };
    }, [schools]);

    // derived state: Filtered Schools
    // This replaces the useEffect + setFilteredSchools pattern
    const filteredSchools = useMemo(() => {
        return schools.filter(school => {
            const matchesSearch = !searchQuery ||
                school.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                school.district?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                school.city?.toLowerCase().includes(searchQuery.toLowerCase());

            const matchesDistrict = selectedDistrict === 'all' || school.district === selectedDistrict;
            const matchesType = selectedType === 'all' || school.type === selectedType;
            const matchesZone = selectedZone === 'all' || school.zone === selectedZone;

            return matchesSearch && matchesDistrict && matchesType && matchesZone;
        });
    }, [searchQuery, selectedDistrict, selectedType, selectedZone, schools]);

    return {
        schools,
        filteredSchools,
        loading,
        searchQuery,
        setSearchQuery,
        selectedDistrict,
        setSelectedDistrict,
        selectedType,
        setSelectedType,
        selectedZone,
        setSelectedZone,
        districts,
        types,
        zones,
        fetchSchools,
    };
};

export default useSchoolData;