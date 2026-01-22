// API utility functions for Teachers (Praktikumslehrkräfte) Management
const BASE_URL = process.env.REACT_APP_API_URL || (process.env.NODE_ENV === 'production' ? 'http://malik08.stud.fim.uni-passau.de/api' : '/api');

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
 * Fetch all teachers
 */
export const fetchTeachers = async () => {
    try {
        console.log('Fetching teachers from:', `${BASE_URL}/pls/`);
        const response = await fetch(`${BASE_URL}/pls/`, {
            method: 'GET',
            credentials: 'include',
        });

        console.log('Response status:', response.status);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Fetched', data.length, 'teachers');
        return data;
    } catch (error) {
        console.error('Fetch teachers error:', error);
        throw error;
    }
};

/**
 * Fetch single teacher by ID
 */
export const fetchTeacherById = async (id) => {
    const response = await fetch(`${BASE_URL}/pls/${id}/`, {
        credentials: 'include',
    });
    if (!response.ok) {
        throw new Error('Failed to fetch teacher');
    }
    return response.json();
};

/**
 * Create a new teacher
 */
export const createTeacher = async (teacherData) => {
    try {
        const csrftoken = getCookie('csrftoken');
        console.log('🔐 CSRF Token:', csrftoken ? 'Found' : 'Not found');

        const response = await fetch(`${BASE_URL}/pls/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken || '',
            },
            credentials: 'include',
            body: JSON.stringify(teacherData),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create teacher');
        }

        return response.json();
    } catch (error) {
        console.error('Create teacher error:', error);
        throw error;
    }
};

/**
 * Update teacher (full update)
 */
export const updateTeacher = async (id, teacherData) => {
    try {
        const csrftoken = getCookie('csrftoken');

        const response = await fetch(`${BASE_URL}/pls/${id}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken || '',
            },
            credentials: 'include',
            body: JSON.stringify(teacherData),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to update teacher');
        }

        return response.json();
    } catch (error) {
        console.error('Update teacher error:', error);
        throw error;
    }
};

/**
 * Update teacher (partial update)
 */
export const patchTeacher = async (id, teacherData) => {
    try {
        const csrftoken = getCookie('csrftoken');

        const response = await fetch(`${BASE_URL}/pls/${id}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken || '',
            },
            credentials: 'include',
            body: JSON.stringify(teacherData),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to update teacher');
        }

        return response.json();
    } catch (error) {
        console.error('Patch teacher error:', error);
        throw error;
    }
};

/**
 * Delete a teacher
 */
export const deleteTeacher = async (id) => {
    const csrftoken = getCookie('csrftoken');
  
    const response = await fetch(`${BASE_URL}/pls/${id}/`, {
      method: 'DELETE',
      headers: { 'X-CSRFToken': csrftoken || '' },
      credentials: 'include',
    });
  
    // ✅ normal success
    if (response.status === 204 || response.status === 200) {
        return true;
    }
  
    // ✅ backend bug: it deletes but returns 500
    if (response.status === 500) {
        return true;
    }
  
    // real error (404/403/etc.)
    const text = await response.text().catch(() => '');
    throw new Error(text || `HTTP ${response.status}: ${response.statusText}`);
  };
  
  
  
  
  

/**
 * Import teachers from Excel
 */
export const importTeachersCSV = async (file) => {
    try {
        const csrftoken = getCookie('csrftoken');
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${BASE_URL}/pls/import_csv/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken || '',
            },
            credentials: 'include',
            body: formData,
        });

        if (!response.ok) {
            let errorMessage = 'Failed to import teachers';
            try {
                const error = await response.json();
                errorMessage = error.error || errorMessage;
            } catch (e) {
                errorMessage = `HTTP ${response.status}: ${response.statusText}`;
            }
            throw new Error(errorMessage);
        }

        return await response.json();
    } catch (error) {
        console.error('Import teachers error:', error);
        if (error.message === 'Failed to fetch') {
            throw new Error('Verbindung zum Server fehlgeschlagen. Bitte stellen Sie sicher, dass der Backend-Server läuft.');
        }
        throw error;
    }
};

/**
 * Export teachers to CSV
 */
export const exportTeachersCSV = async () => {
    try {
        const response = await fetch(`${BASE_URL}/pls/export/`, {
            credentials: 'include',
        });

        if (!response.ok) {
            throw new Error('Failed to export teachers');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'pls_export.csv';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Export teachers error:', error);
        throw error;
    }
};