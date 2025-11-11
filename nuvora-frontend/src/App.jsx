import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import StartShiftPage from './pages/StartShiftPage';
import HomePage from './pages/HomePage';
import VehiculosPage from './pages/VehiculosPage';
import ActividadPage from './pages/ActividadPage';
import BaseDatosPage from './pages/BaseDatosPage';
import DashboardLayout from './layouts/DashboardLayout';

function RequireAuth({ children }) {
  const token = localStorage.getItem("token");
  if (!token) return <Navigate to="/" replace />;
  return children;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Login */}
        <Route path="/" element={<LoginPage />} />
        <Route path="/login" element={<LoginPage />} />

        {/* Iniciar turno */}
        <Route 
          path="/start-shift" 
          element={
            <RequireAuth>
              <StartShiftPage />
            </RequireAuth>
          } 
        />

        {/* Dashboard con Sidebar */}
        <Route path="/dashboard" element={<DashboardLayout />}>
          <Route index element={<HomePage />} />
          <Route path="vehiculos" element={<VehiculosPage />} />
          <Route path="actividad" element={<ActividadPage />} />
          <Route path="bd" element={<BaseDatosPage />} />
        </Route>

        {/* Redirección por defecto */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
