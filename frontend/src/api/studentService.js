import api from './config';

export const studentService = {
  getAll: (params = {}) => {
    return api.get('/students/', { params });
  },

  getById: (id) => {
    return api.get(`/students/${id}/`);
  },

  create: (data) => {
    return api.post('/students/', data);
  },

  update: (id, data) => {
    return api.put(`/students/${id}/`, data);
  },

  partialUpdate: (id, data) => {
    return api.patch(`/students/${id}/`, data);
  },

  delete: (id) => {
    return api.delete(`/students/${id}/`);
  },

  search: (searchTerm, params = {}) => {
    return api.get('/students/', { 
      params: { 
        search: searchTerm,
        ...params 
      } 
    });
  },

  exportCSV: () => {
    return api.get('/students/export/', {
      responseType: 'blob',
    });
  },

  importCSV: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/students/import_csv/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  exportExcel: () => {
    return api.get('/students/export_excel/', {
      responseType: 'blob',
    });
  },

  importExcel: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/students/import_excel/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Student assignment methods
  assignStudent: (studentId, assignmentData) => {
    return api.post(`/students/${studentId}/assign/`, assignmentData);
  },

  reassignStudent: (studentId, assignmentData) => {
    return api.post(`/students/${studentId}/reassign/`, assignmentData);
  },

  removeAssignment: (studentId, assignmentData) => {
    return api.post(`/students/${studentId}/remove_assignment/`, assignmentData);
  },

  getAssignment: (studentId) => {
    return api.get(`/students/${studentId}/assignment/`);
  },

  getUnassignedStudents: (params = {}) => {
    return api.get('/students/unassigned/', { params });
  },
};

export default studentService;

