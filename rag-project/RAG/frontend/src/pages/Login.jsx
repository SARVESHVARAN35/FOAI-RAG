import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import Notice from '../components/common/Notice.jsx'
import { useAuth } from '../auth/useAuth.js'

function Login() {
  const { login } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const notice = location.state?.message || ''
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      await login({ email, password })
      navigate(location.state?.from?.pathname || '/dashboard', { replace: true })
    } catch (requestError) {
      setError(requestError.message || 'Unable to sign in.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="surface auth-card">
        <div className="auth-heading">
          <div className="page-eyebrow">Enterprise IT Knowledge Assistant</div>
          <h1 className="page-title">Sign in</h1>
          <p className="page-description">Use your account to continue to the incident assistant.</p>
        </div>
        {notice && <Notice tone="success">{notice}</Notice>}
        {error && <Notice tone="error">{error}</Notice>}
        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="field">
            <span className="field-label">Email</span>
            <input
              className="input"
              type="email"
              autoComplete="username"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>
          <label className="field">
            <span className="field-label">Password</span>
            <input
              className="input"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          <button className="button button-primary auth-submit" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
        <p className="auth-footer">Need an account? <Link to="/register">Register</Link></p>
      </section>
    </main>
  )
}

export default Login
