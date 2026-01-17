import api from './config';

export const schoolService = {
  getAll: (params = {}) => {
    return api.get('/schools/', { params });
  },

  getById: (id) => {
    return api.get(`/schools/${id}/`);
  },

  create: (data) => {
    return api.post('/schools/', data);
  },

  update: (id, data) => {
    return api.put(`/schools/${id}/`, data);
  },

  partialUpdate: (id, data) => {
    return api.patch(`/schools/${id}/`, data);
  },

  delete: (id) => {
    return api.delete(`/schools/${id}/`);
  },

  search: (searchTerm, params = {}) => {
    return api.get('/schools/', { 
      params: { 
        search: searchTerm,
        ...params 
      } 
    });
  },

  exportCSV: () => {
    return api.get('/schools/export/', {
      responseType: 'blob',
    });
  },

  importCSV: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/schools/import_csv/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

export default schoolService;
