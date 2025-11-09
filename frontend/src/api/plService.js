import api from './config';

export const plService = {
  getAll: (params = {}) => {
    return api.get('/pls/', { params });
  },

  getById: (id) => {
    return api.get(`/pls/${id}/`);
  },

  create: (data) => {
    return api.post('/pls/', data);
  },

  update: (id, data) => {
    return api.put(`/pls/${id}/`, data);
  },

  partialUpdate: (id, data) => {
    return api.patch(`/pls/${id}/`, data);
  },

  delete: (id) => {
    return api.delete(`/pls/${id}/`);
  },

  search: (searchTerm, params = {}) => {
    return api.get('/pls/', { 
      params: { 
        search: searchTerm,
        ...params 
      } 
    });
  },
};

export default plService;

