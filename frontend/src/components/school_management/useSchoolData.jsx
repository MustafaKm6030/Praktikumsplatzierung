import { useState, useEffect, useCallback } from 'react';

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
 * Custom hook for managing school data
 * @returns {Object} School management state and functions
 */
const useSchoolData = () => {
    /** @type {[School[], React.Dispatch<React.SetStateAction<School[]>>]} */
    const [schools, setSchools] = useState([]);
    /** @type {[School[], React.Dispatch<React.SetStateAction<School[]>>]} */
    const [filteredSchools, setFilteredSchools] = useState([]);
    const [loading, setLoading] = useState(false);

    // Filter states
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedDistrict, setSelectedDistrict] = useState('all');
    const [selectedType, setSelectedType] = useState('all');
    const [selectedZone, setSelectedZone] = useState('all');

    // Unique filter options
    const [districts, setDistricts] = useState([]);
    const [types, setTypes] = useState([]);
    const [zones, setZones] = useState([]);

    /**
     * Extract unique filter values from schools data
     * @param {School[]} data
     */
    const extractFilterOptions = useCallback((data) => {
        const uniqueDistricts = [...new Set(data.map(s => s.district).filter(Boolean))];
        const uniqueTypes = [...new Set(data.map(s => s.school_type).filter(Boolean))];
        const uniqueZones = [...new Set(data.map(s => s.zone).filter(Boolean))].sort((a, b) => a - b);

        setDistricts(uniqueDistricts);
        setTypes(uniqueTypes);
        setZones(uniqueZones);
    }, []);

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

                setLoading(false);
                return;
            }
            const data = await response.json();
            setSchools(data);
            setFilteredSchools(data);
            extractFilterOptions(data);
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
        } finally {
            setLoading(false);
        }
    }, [extractFilterOptions]);

    // Initial fetch
    useEffect(() => {
        void fetchSchools();
    }, [fetchSchools]);

    // Apply filters
    useEffect(() => {
        let filtered = schools;

        if (searchQuery) {
            filtered = filtered.filter(school =>
                school.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                school.district?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                school.city?.toLowerCase().includes(searchQuery.toLowerCase())
            );
        }

        if (selectedDistrict !== 'all') {
            filtered = filtered.filter(school => school.district === selectedDistrict);
        }

        if (selectedType !== 'all') {
            filtered = filtered.filter(school => school.school_type === selectedType);
        }

        if (selectedZone !== 'all') {
            filtered = filtered.filter(school => school.zone === parseInt(selectedZone, 10));
        }

        setFilteredSchools(filtered);
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