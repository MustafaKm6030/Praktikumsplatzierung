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
        return api.post('/assignments/run-solver/', payload, {
            timeout: 300000
        });
    },

    /**
     * Fetch the results of the allocation.
     * Endpoint: GET /api/assignments/
     */
    getAssignments: (params = {}) => {
        return api.get('/assignments/', { params });
    },

    /**
     * Export assignments as Excel file.
     * Endpoint: GET /api/assignments/export/excel/
     */
    exportExcel: () => {
        return api.get('/assignments/export/excel/', {
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
    },

    /**
     * Get detailed statistics about assignments.
     * Endpoint: GET /api/assignments/statistics/
     */
    getStatistics: () => {
        return api.get('/assignments/statistics/');
    }
};

export default allocationService;