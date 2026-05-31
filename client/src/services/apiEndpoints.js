// Use a same-origin path in local dev so Vite can proxy API requests and avoid browser CORS.
const isLocalDev =
  typeof window !== 'undefined' && ['localhost', '127.0.0.1'].includes(window.location.hostname)

const API_URL = isLocalDev ? '' : import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// API Endpoints
export const API_ENDPOINTS = {
  // Auth endpoints
  AUTH: {
    LOGIN: `${API_URL}/auth/login`,
    SIGNUP: `${API_URL}/auth/signup`,
    LOGOUT: `${API_URL}/auth/logout`,
    REFRESH: `${API_URL}/auth/refresh`,
    PROFILE: `${API_URL}/auth/profile`,
  },

  // Chat endpoints
  CHAT: {
    GET: `${API_URL}/chat`,        // GET all chats, POST new chat, GET/PUT/DELETE individual chat
    MESSAGE: `${API_URL}/chat/message`, // POST send message (MAIN ENDPOINT)
    LIST: `${API_URL}/chat`,       // GET chat list
    CREATE: `${API_URL}/chat`,     // POST create chat
    DELETE: `${API_URL}/chat`,     // DELETE chat
    SEND: `${API_URL}/chat/message`,     // POST send message
    UPLOAD: `${API_URL}/chat/upload`,    // POST upload files
  },

  // Upload endpoints
  UPLOAD: {
    FILE: `${API_URL}/upload`,
    MULTIPLE: `${API_URL}/upload`,
  },
}
