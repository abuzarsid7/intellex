import { useEffect, useMemo, useState } from 'react'
import { AuthContext } from '../../context/AuthContext.jsx'
import api from '../../services/axios'
import { API_ENDPOINTS } from '../../services/apiEndpoints'

const AUTH_TOKEN_KEY = 'auth_token'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  const getStoredToken = () =>
    typeof window !== 'undefined' ? window.localStorage.getItem(AUTH_TOKEN_KEY) : null

  const storeToken = (token) => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(AUTH_TOKEN_KEY, token)
    }
  }

  const clearToken = () => {
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem(AUTH_TOKEN_KEY)
    }
  }

  // Check if user is already logged in on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = getStoredToken()

      if (!token) {
        setUser(null)
        setIsLoading(false)
        return
      }

      try {
        const response = await api.get(API_ENDPOINTS.AUTH.PROFILE)
        setUser(response.data.user)
        setError(null)
      } catch (err) {
        setUser(null)
        clearToken()
        // User is not authenticated, which is expected
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  const register = async (name, email, password) => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await api.post(API_ENDPOINTS.AUTH.SIGNUP, {
        name,
        email,
        password,
      })
      const token = response.data.access_token
      if (token) {
        storeToken(token)
      }
      setUser(response.data.user)
      return response.data
    } catch (err) {
      const message = err.response?.data?.message || 'Registration failed'
      setError(message)
      throw new Error(message)
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email, password) => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await api.post(API_ENDPOINTS.AUTH.LOGIN, {
        email,
        password,
      })
      const token = response.data.access_token
      if (token) {
        storeToken(token)
      }
      setUser(response.data.user)
      return response.data
    } catch (err) {
      const message = err.response?.data?.message || 'Login failed'
      setError(message)
      throw new Error(message)
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    setIsLoading(true)
    try {
      await api.post(API_ENDPOINTS.AUTH.LOGOUT)
      clearToken()
      setUser(null)
      setError(null)
    } catch (err) {
      console.error('Logout failed:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const value = useMemo(
    () => ({
      user,
      isLoading,
      error,
      isAuthenticated: !!user,
      register,
      login,
      logout,
      setError,
    }),
    [user, isLoading, error]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
