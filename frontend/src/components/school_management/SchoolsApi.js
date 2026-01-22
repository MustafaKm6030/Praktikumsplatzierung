// API utility functions for Schools Management
const BASE_URL = process.env.REACT_APP_API_URL || (process.env.NODE_ENV === 'production' ? 'http://malik08.stud.fim.uni-passau.de/api' : '/api');

console.log('🔗 API Base URL:', BASE_URL);

/**
 * Get CSRF token from cookie
 */
function getCookie(name) {
    if (!document.cookie) {
        return null;
    }
    
    const cookie = document.cookie
        .split(';')
        .map(c => c.trim())
        .find(c => c.startsWith(name + '='));
        
    return cookie ? decodeURIComponent(cookie.substring(name.length + 1)) : null;
}

/**
 * Helper: Generic Request Handler to reduce code duplication
 */
async function sendRequest(endpoint, method, data = null) {
    try {
        const csrftoken = getCookie('csrftoken');
        const config = {
            method,
            headers: {
                'X-CSRFToken': csrftoken || '',
            },
            credentials: 'include',
        };

        if (data) {
            config.headers['Content-Type'] = 'application/json';
            config.body = JSON.stringify(data);
        }

        const response = await fetch(`${BASE_URL}${endpoint}`, config);

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.error || `Request failed: ${response.statusText}`);
        }

        // Handle 204 No Content (common for Delete/Update)
        if (response.status === 204) {
            return true;
        }

        return await response.json();
    } catch (error) {
        console.error(`${method} request error:`, error);
        throw error;
    }
}

/**
 * Fetch all schools
 */
export const fetchSchools = async () => {
    try {
        const response = await fetch(`${BASE_URL}/schools/`, {
            method: 'GET',
            credentials: 'include',
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Fetch schools error:', error);
        throw error;
    }
};

/**
 * Fetch single school by ID
 */
export const fetchSchoolById = async (id) => {
    const response = await fetch(`${BASE_URL}/schools/${id}/`, {
        credentials: 'include',
    });
    if (!response.ok) {
        throw new Error('Failed to fetch school');
    }
    return response.json();
};

/**
 * Create a new school
 */
export const createSchool = (schoolData) => {
    return sendRequest('/schools/', 'POST', schoolData);
};

/**
 * Update school (full update)
 */
export const updateSchool = (id, schoolData) => {
    return sendRequest(`/schools/${id}/`, 'PUT', schoolData);
};

/**
 * Update school (partial update)
 */
export const patchSchool = (id, schoolData) => {
    return sendRequest(`/schools/${id}/`, 'PATCH', schoolData);
};

/**
 * Delete a school (soft delete - sets is_active=False)
 */
export const deleteSchool = async (id) => {
    try {
        const csrftoken = getCookie('csrftoken');

        const response = await fetch(`${BASE_URL}/schools/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrftoken || '',
            },
            credentials: 'include',
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.error || 'Failed to delete school');
        }

        // Backend returns 200 with message for soft delete
        return response.json();
    } catch (error) {
        console.error('Delete school error:', error);
        throw error;
    }
};

/**
 * Import schools from CSV
 */
export const importSchoolsCSV = async (file) => {
    try {
        const csrftoken = getCookie('csrftoken');
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${BASE_URL}/schools/import_csv/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken || '',
            },
            credentials: 'include',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to import schools');
        }

        return response.json();
    } catch (error) {
        console.error('Import schools error:', error);
        throw error;
    }
};

/**
 * Export schools to Excel
 */
export const exportSchoolsExcel = async () => {
    try {
        const response = await fetch(`${BASE_URL}/schools/export/`, {
            credentials: 'include',
        });

        if (!response.ok) {
            throw new Error('Failed to export schools');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'schools_export.xlsx';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Export schools error:', error);
        throw error;
    }
};

export const runGeocodingTask = async () => {
    try {
        return await sendRequest('/schools/run_geocoding_task/', 'POST');
    } catch (error) {
        console.error('Run geocoding task error:', error);
        throw error;
    }
};