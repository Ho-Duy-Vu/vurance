import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000',
  withCredentials: true,
});

function getCsrfToken(): string {
  if (typeof document === 'undefined') return '';
  const match = document.cookie.match(/csrf_token=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : '';
}

api.interceptors.request.use((config) => {
  if (['post', 'put', 'delete', 'patch'].includes((config.method ?? '').toLowerCase())) {
    config.headers['X-CSRF-Token'] = getCsrfToken();
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && typeof window !== 'undefined') {
      const lang = document.documentElement.lang || 'vi';
      window.location.href = `/${lang}/login`;
    }
    return Promise.reject(err);
  }
);

export default api;
