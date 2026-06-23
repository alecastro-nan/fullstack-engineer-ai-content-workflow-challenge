import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30_000,
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
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

async function graphqlRequest<T>(
  query: string,
  variables?: Record<string, unknown>,
): Promise<T> {
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
