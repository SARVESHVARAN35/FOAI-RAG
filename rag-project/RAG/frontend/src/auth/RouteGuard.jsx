import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './useAuth.js'

export function RequireAuth({ children, allowedRoles }) {
  const { user, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return <div className="auth-loading" role="status">Checking sign-in...</div>
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />
  }

  return children
}

export function PublicOnly({ children }) {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return <div className="auth-loading" role="status">Checking sign-in...</div>
  }

  return user ? <Navigate to="/dashboard" replace /> : children
}
