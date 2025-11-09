import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorMessage = getErrorMessage(error);
    console.error('API Error:', errorMessage);
    return Promise.reject(error);
  }
);

export const getErrorMessage = (error) => {
  if (error.response) {
    if (error.response.data?.message) {
      return error.response.data.message;
    }
    if (error.response.data?.error) {
      return error.response.data.error;
    }
    if (typeof error.response.data === 'string') {
      return error.response.data;
    }
    switch (error.response.status) {
      case 400:
        return 'Invalid request. Please check your input.';
      case 401:
        return 'Unauthorized. Please log in.';
      case 403:
        return 'You do not have permission to perform this action.';
      case 404:
        return 'Resource not found.';
      case 500:
        return 'Server error. Please try again later.';
      default:
        return `Error: ${error.response.status} ${error.response.statusText}`;
    }
  } else if (error.request) {
    return 'Network error. Please check your connection and ensure the backend is running.';
  }
  return error.message || 'An unexpected error occurred.';
};

export default api;

