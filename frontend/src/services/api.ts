import axios from 'axios';
import { authService } from './auth';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30_000,
});

apiClient.interceptors.request.use(
  (config) => {
    const token = authService.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authService.clearTokens();
    }
    if (error.response && import.meta.env.DEV) {
      console.error('API Error:', error.response.status, error.response.data);
    }
    return Promise.reject(error);
  },
);

interface GraphQLResponse<T> {
  data?: T;
  errors?: Array<{ message: string }>;
}

async function graphqlRequest<T>(query: string, variables?: Record<string, unknown>): Promise<T> {
  const response = await apiClient.post<GraphQLResponse<T>>('/graphql', {
    query,
    variables,
  });

  const body = response.data;
  if (body.errors) {
    throw new Error(body.errors[0]?.message ?? 'GraphQL error');
  }
  if (!body.data) {
    throw new Error('No data returned from GraphQL');
  }
  return body.data;
}

export { apiClient, graphqlRequest };
