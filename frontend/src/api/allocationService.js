import api from './config';

const allocationService = {
    /**
     * Fetch demand preview data for allocation page.
     * Endpoint: GET /api/assignments/demand-preview/
     */
    getDemandPreview: () => {
        return api.get('/assignments/demand-preview/');
    },

    /**
     * Trigger the auto-allocation algorithm.
     * Endpoint: POST /api/assignments/run-solver/
     */
    runAutoAllocation: (payload = {}) => {
        return api.post('/assignments/run-solver/', payload);
    },

    /**
     * Fetch the results of the allocation.
     * Endpoint: GET /api/assignments/
     */
    getAssignments: (params = {}) => {
        return api.get('/assignments/', { params });
    },

    /**
     * Export assignments as CSV file.
     * Endpoint: GET /api/assignments/export/csv/
     */
    exportCSV: () => {
        return api.get('/assignments/export/csv/', {
            responseType: 'blob'
        });
    },

    /**
     * Export assignments as PDF file.
     * Endpoint: GET /api/assignments/export/pdf/
     */
    exportPDF: () => {
        return api.get('/assignments/export/pdf/', {
            responseType: 'blob'
        });
    }
};

export default allocationService;