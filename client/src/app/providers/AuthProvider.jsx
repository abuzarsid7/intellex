import { useEffect, useMemo, useState } from 'react'
import { AuthContext } from '../../context/AuthContext.jsx'
import api from '../../services/axios'
import { API_ENDPOINTS } from '../../services/apiEndpoints'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  const hasActiveSessionCookie = () =>
    typeof document !== 'undefined' && document.cookie.includes('logged_in=true')

  // Check if user is already logged in on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (!hasActiveSessionCookie()) {
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
