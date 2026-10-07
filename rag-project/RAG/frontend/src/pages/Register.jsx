import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Notice from '../components/common/Notice.jsx'
import { useAuth } from '../auth/useAuth.js'

function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    role: 'SUPPORT_ENGINEER',
  })
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  function setField(field) {
    return (event) => setForm((current) => ({ ...current, [field]: event.target.value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      await register(form)
      navigate('/login', {
        replace: true,
        state: { message: 'Account created. Sign in with your new account.' },
      })
    } catch (requestError) {
      setError(requestError.message || 'Unable to create the account.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="surface auth-card">
        <div className="auth-heading">
          <div className="page-eyebrow">Enterprise IT Knowledge Assistant</div>
          <h1 className="page-title">Create account</h1>
          <p className="page-description">New accounts are registered as Support Engineers.</p>
        </div>
        {error && <Notice tone="error">{error}</Notice>}
        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="field">
            <span className="field-label">Name</span>
            <input className="input" autoComplete="name" value={form.name} onChange={setField('name')} required maxLength={200} />
          </label>
          <label className="field">
            <span className="field-label">Email</span>
            <input className="input" type="email" autoComplete="email" value={form.email} onChange={setField('email')} required maxLength={320} />
          </label>
          <label className="field">
            <span className="field-label">Password</span>
            <input
              className="input"
              type="password"
              autoComplete="new-password"
              value={form.password}
              onChange={setField('password')}
              required
              minLength={8}
              maxLength={72}
            />
            <span className="field-help">Use 8–72 characters.</span>
          </label>
          <label className="field">
            <span className="field-label">Role</span>
            <select className="select" value={form.role} onChange={setField('role')}>
              <option value="SUPPORT_ENGINEER">Support Engineer</option>
            </select>
          </label>
          <button className="button button-primary auth-submit" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Creating account...' : 'Register'}
          </button>
        </form>
        <p className="auth-footer">Already registered? <Link to="/login">Sign in</Link></p>
      </section>
    </main>
  )
}

export default Register
