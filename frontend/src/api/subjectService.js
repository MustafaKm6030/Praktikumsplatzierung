import api from './config';

export const subjectService = {
  getAll: () => {
    return api.get('/subjects/');
  },

  getById: (id) => api.get(`/subjects/${id}/`),

  getActive: () => {
    return api.get('/subjects/?is_active=true');
  },

  getFromRules: () => {
    return api.get('/subjects/from_rules/');
  },

  create: (data) => api.post('/subjects/', data),

  update: (id, data) => {
    return api.put(`/subjects/${id}/`, data);
  },

  partialUpdate: (id, data) => {
    return api.patch(`/subjects/${id}/`, data);
  },

  delete: (id) => api.delete(`/subjects/${id}/`),

  getPraktikumTypes: () => {
    return api.get('/praktikum-types/');
  },
};

export default subjectService;
