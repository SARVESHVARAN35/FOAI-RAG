const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000')
  .replace(/\/+$/, '')
const BACKEND_STATUS_EVENT = 'ops-knowledge:backend-status'
const AUTH_TOKEN_KEY = 'ops-knowledge:token'

export function getAuthToken() {
  return localStorage.getItem(AUTH_TOKEN_KEY)
}

export function saveAuthSession(accessToken, user) {
  localStorage.setItem(AUTH_TOKEN_KEY, accessToken)
  localStorage.setItem('ops-knowledge:user', JSON.stringify(user))
}

export function saveCurrentUser(user) {
  localStorage.setItem('ops-knowledge:user', JSON.stringify(user))
}

export function getStoredUser() {
  const storedUser = localStorage.getItem('ops-knowledge:user')
  if (!storedUser) return null

  try {
    return JSON.parse(storedUser)
  } catch {
    localStorage.removeItem('ops-knowledge:user')
    return null
  }
}

export function clearAuthSession() {
  localStorage.removeItem(AUTH_TOKEN_KEY)
  localStorage.removeItem('ops-knowledge:user')
}

function reportBackendStatus(online) {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent(BACKEND_STATUS_EVENT, { detail: { online } }))
  }
}

export class ApiError extends Error {
  constructor(message, status = 0) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function request(path, options = {}, errorMessages = {}) {
  let response

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        Accept: 'application/json',
        ...options.headers,
        ...(getAuthToken()
          ? { Authorization: `Bearer ${getAuthToken()}` }
          : {}),
      },
    })
  } catch {
    reportBackendStatus(false)
    throw new ApiError(
      'Unable to connect to the backend. Please make sure the FastAPI server is running.',
    )
  }

  reportBackendStatus(true)

  if (!response.ok) {
    const messages = {
      400: 'The backend could not accept this request. Check the submitted information and try again.',
      401: 'Your email or password is incorrect, or your sign-in has expired.',
      403: 'You do not have permission to perform this action.',
      404: 'This backend route is not available.',
      409: 'A user with this email already exists.',
      500: 'The backend encountered an error while processing the request. Please try again later.',
    }
    throw new ApiError(
      errorMessages[response.status] ||
        messages[response.status] ||
        `The backend request failed (${response.status}).`,
      response.status,
    )
  }

  try {
    return await response.json()
  } catch {
    throw new ApiError('The backend returned an unreadable response.', response.status)
  }
}

export function loginUser(credentials) {
  return request('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  })
}

export function registerUser(user) {
  return request('/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(user),
  })
}

export function getCurrentUser() {
  return request('/auth/me')
}

export function queryRAG(query) {
  return request('/rag/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })
}

export function getKnowledgeDocuments() {
  return request('/knowledge')
}

export function uploadKnowledgePdf(file) {
  const formData = new FormData()
  formData.append('file', file)

  return request(
    '/knowledge/pdf',
    {
      method: 'POST',
      body: formData,
    },
    {
      400: 'The selected file must be a PDF.',
      500: 'The PDF could not be processed. Please try again.',
    },
  )
}

export function getBackendHealth() {
  return request('/api/health')
}

export function getBackendStatus() {
  return request('/')
}

export { API_BASE_URL, BACKEND_STATUS_EVENT }
