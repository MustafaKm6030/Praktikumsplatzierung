import api from './config';

export const settingsService = {
  getActive: () => {
    return api.get('/settings/');
  },

  getById: (id) => {
    return api.get(`/settings/${id}/`);
  },

  getAll: () => {
    return api.get('/settings/all/');
  },

  create: (data) => {
    return api.post('/settings/', data);
  },

  update: (id, data) => {
    return api.put(`/settings/${id}/`, data);
  },

  partialUpdate: (id, data) => {
    return api.patch(`/settings/${id}/`, data);
  },

  delete: (id) => {
    return api.delete(`/settings/${id}/`);
  },

  getBudgetAllocation: (id) => {
    return api.get(`/settings/${id}/budget_allocation/`);
  },
};

export default settingsService;

