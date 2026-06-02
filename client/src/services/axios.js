import axios from "axios";

const isLocalDev =
  typeof window !== 'undefined' && ['localhost', '127.0.0.1'].includes(window.location.hostname)

const api = axios.create({
  baseURL: isLocalDev ? '/api' : import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = window.localStorage.getItem('auth_token')

    if (token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${token}`
    }
  }

  return config
});

export default api;