import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './auth/AuthContext.jsx'
import { PublicOnly, RequireAuth } from './auth/RouteGuard.jsx'
import AppLayout from './components/layout/AppLayout.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Incidents from './pages/Incidents.jsx'
import IncidentForm from './pages/IncidentForm.jsx'
import IncidentDetails from './pages/IncidentDetails.jsx'
import IncidentAssistant from './pages/IncidentAssistant.jsx'
import Resolutions from './pages/Resolutions.jsx'
import Reviews from './pages/Reviews.jsx'
import KnowledgeBase from './pages/KnowledgeBase.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Settings from './pages/Settings.jsx'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<PublicOnly><Login /></PublicOnly>} />
          <Route path="/register" element={<PublicOnly><Register /></PublicOnly>} />
          <Route element={<RequireAuth><AppLayout /></RequireAuth>}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/incidents" element={<Incidents />} />
            <Route path="/incidents/new" element={<IncidentForm />} />
            <Route path="/incidents/:id" element={<IncidentDetails />} />
            <Route path="/assistant" element={<IncidentAssistant />} />
            <Route path="/resolutions" element={<Resolutions />} />
            <Route
              path="/reviews"
              element={<RequireAuth allowedRoles={['IT_LEAD', 'ADMIN']}><Reviews /></RequireAuth>}
            />
            <Route
              path="/knowledge"
              element={<RequireAuth allowedRoles={['ADMIN']}><KnowledgeBase /></RequireAuth>}
            />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
