import { useState, useEffect, useCallback, useMemo } from 'react';

const BASE_URL = 'http://malik08.stud.fim.uni-passau.de/api';

/**
 * Custom hook for managing school data.
 */
const useSchoolData = () => {
    const [schools, setSchools] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Filter state
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedDistrict, setSelectedDistrict] = useState('all');
    const [selectedType, setSelectedType] = useState('all');
    const [selectedZone, setSelectedZone] = useState('all');

    // Fetch schools from API
    const fetchSchools = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            console.log('Fetching schools from:', `${BASE_URL}/schools/`);

            const response = await fetch(`api/schools/`, {
                method: 'GET',
                credentials: 'include', // IMPORTANT: Include cookies
            });

            console.log('Response status:', response.status);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Fetched', data.length, 'schools');
            setSchools(Array.isArray(data) ? data : []);

        } catch (err) {
            console.error('Error fetching schools:', err);
            setError(err.message);
            setSchools([]);
        } finally {
            setLoading(false);
        }
    }, []);

    // Initial data fetch
    useEffect(() => {
        fetchSchools();
    }, [fetchSchools]);

    // Unique filter options
    const { districts, types, zones } = useMemo(() => {
        const uniqueDistricts = [...new Set(schools.map(s => s.district).filter(Boolean))].sort();
        const uniqueTypes = [...new Set(schools.map(s => s.school_type).filter(Boolean))].sort();
        const uniqueZones = [...new Set(schools.map(s => s.zone).filter(Boolean))].sort((a, b) => a - b);

        return { districts: uniqueDistricts, types: uniqueTypes, zones: uniqueZones };
    }, [schools]);

    // Filtered schools
    const filteredSchools = useMemo(() => {
        return schools.filter(school => {
            const matchesSearch = !searchQuery ||
                school.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                school.district?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                school.city?.toLowerCase().includes(searchQuery.toLowerCase());

            const matchesDistrict = selectedDistrict === 'all' || school.district === selectedDistrict;
            const matchesType = selectedType === 'all' || school.school_type === selectedType;
            const matchesZone = selectedZone === 'all' || school.zone === parseInt(selectedZone, 10);

            return matchesSearch && matchesDistrict && matchesType && matchesZone;
        });
    }, [searchQuery, selectedDistrict, selectedType, selectedZone, schools]);

    return {
        schools,
        loading,
        error,
        fetchSchools,
        filteredSchools,
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
    };
};

export default useSchoolData;