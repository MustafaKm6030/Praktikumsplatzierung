import api from './config';

export const subjectService = {
  getAll: () => {
    return api.get('/subjects/');
  },

  getById: (id) => {
    return api.get(`/subjects/${id}/`);
  },

  getActive: () => {
    return api.get('/subjects/?is_active=true');
  },

  getFromRules: () => {
    return api.get('/subjects/from_rules/');
  },

  create: (data) => {
    return api.post('/subjects/', data);
  },

  update: (id, data) => {
    return api.put(`/subjects/${id}/`, data);
  },

  partialUpdate: (id, data) => {
    return api.patch(`/subjects/${id}/`, data);
  },

  delete: (id) => {
    return api.delete(`/subjects/${id}/`);
  },
};

export default subjectService;
