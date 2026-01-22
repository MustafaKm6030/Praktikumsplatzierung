// API utility functions for Schools Management
const BASE_URL = process.env.REACT_APP_API_URL || (process.env.NODE_ENV === 'production' ? 'http://malik08.stud.fim.uni-passau.de/api' : '/api');

console.log('🔗 API Base URL:', BASE_URL);

/**
 * Get CSRF token from cookie
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Fetch all schools
 */
export const fetchSchools = async () => {
    try {
        console.log('Fetching schools from:', `${BASE_URL}/schools/`);
        const response = await fetch(`${BASE_URL}/schools/`, {
            method: 'GET',
            credentials: 'include',
        });

        console.log('Response status:', response.status);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Fetched', data.length, 'schools');
        return data;
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
export const createSchool = async (schoolData) => {
    try {
        const csrftoken = getCookie('csrftoken');
        console.log('🔐 CSRF Token:', csrftoken ? 'Found' : 'Not found');

        const response = await fetch(`${BASE_URL}/schools/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken || '',
            },
            credentials: 'include',
            body: JSON.stringify(schoolData),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create school');
        }

        return response.json();
    } catch (error) {
        console.error('Create school error:', error);
        throw error;
    }
};

/**
 * Update school (full update)
 */
export const updateSchool = async (id, schoolData) => {
    try {
        const csrftoken = getCookie('csrftoken');

        const response = await fetch(`${BASE_URL}/schools/${id}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken || '',
            },
            credentials: 'include',
            body: JSON.stringify(schoolData),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to update school');
        }

        return response.json();
    } catch (error) {
        console.error('Update school error:', error);
        throw error;
    }
};

/**
 * Update school (partial update)
 */
export const patchSchool = async (id, schoolData) => {
    try {
        const csrftoken = getCookie('csrftoken');

        const response = await fetch(`${BASE_URL}/schools/${id}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken || '',
            },
            credentials: 'include',
            body: JSON.stringify(schoolData),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to update school');
        }

        return response.json();
    } catch (error) {
        console.error('Patch school error:', error);
        throw error;
    }
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
 * Export schools to CSV
 */
export const exportSchoolsCSV = async () => {
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
        link.download = 'schools_export.csv';
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
        const csrftoken = getCookie('csrftoken');

        // This is a POST request to a custom action
        const response = await fetch(`${BASE_URL}/schools/run_geocoding_task/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken || '',
            },
            credentials: 'include',
        });

        if (!response.ok) {
            // Try to get more detailed error from backend
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
        }

        // Return the success message from the backend
        return response.json();

    } catch (error) {
        console.error('Run geocoding task error:', error);
        throw error;
    }
};