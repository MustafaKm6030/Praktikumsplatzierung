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
    }
};

export default allocationService;