import axios from "axios";

const isLocalDev =
  typeof window !== 'undefined' && ['localhost', '127.0.0.1'].includes(window.location.hostname)

const api = axios.create({
  baseURL: isLocalDev ? '/api' : import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  withCredentials: true, // Enable cookies
});

export default api;