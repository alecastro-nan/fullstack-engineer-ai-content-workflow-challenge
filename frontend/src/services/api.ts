import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // TODO: F-011 — replace with user-facing error toast in production
      console.error(`API Error: ${error.response.status}`, error.response.data);
    }
    return Promise.reject(error);
  },
);

export { apiClient };
