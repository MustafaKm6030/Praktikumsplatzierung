import api from './config';

const allocationService = {
    /**
     * Trigger the auto-allocation algorithm.
     * Endpoint: POST /api/assignments/generate/
     */
    runAutoAllocation: (payload = {}) => {
        return api.post('/assignments/generate/', payload);
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