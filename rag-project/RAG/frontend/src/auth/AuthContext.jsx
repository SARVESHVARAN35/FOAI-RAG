import { useEffect, useMemo, useState } from 'react'
import { AuthContext } from './context.js'
import {
  clearAuthSession,
  getAuthToken,
  getCurrentUser,
  getStoredUser,
  loginUser,
  registerUser,
  saveAuthSession,
  saveCurrentUser,
} from '../services/api.js'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(getStoredUser)
  const [isLoading, setIsLoading] = useState(Boolean(getAuthToken()))

  useEffect(() => {
    if (!getAuthToken()) return undefined

    let active = true
    getCurrentUser()
      .then((currentUser) => {
        if (!active) return
        saveCurrentUser(currentUser)
        setUser(currentUser)
      })
      .catch((error) => {
        if (!active) return
        if (error.status === 401) {
          clearAuthSession()
          setUser(null)
        }
      })
      .finally(() => {
        if (active) setIsLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  async function login(credentials) {
    const result = await loginUser(credentials)
    saveAuthSession(result.access_token, result.user)
    setUser(result.user)
    return result.user
  }

  async function register(userDetails) {
    return registerUser(userDetails)
  }

  function logout() {
    clearAuthSession()
    setUser(null)
  }

  const value = useMemo(
    () => ({ user, isLoading, login, register, logout }),
    [user, isLoading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
