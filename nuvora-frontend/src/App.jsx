import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import StartShiftPage from './pages/StartShiftPage';
import HomePage from './pages/HomePage';
import VehiculosPage from './pages/VehiculosPage';
import BaseDatosPage from './pages/BaseDatosPage';
import TurnosPage from './pages/TurnosPage';
import CerrarTurnoPage from './pages/CerrarTurnoPage';
import HacerCierrePage from './pages/HacerCierrePage';
import CierresPage from './pages/CierresPage';
import UsuariosPage from './pages/UsuariosPage';
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
          <Route path="bd" element={<BaseDatosPage />} />
          <Route path="turnos" element={<TurnosPage />} />
          <Route path="cerrar-turno" element={<CerrarTurnoPage />} />
          <Route path="hacer-cierre" element={<HacerCierrePage />} />
          <Route path="cierres" element={<CierresPage />} />
          <Route path="usuarios" element={<UsuariosPage />} />
        </Route>

        {/* Redirección por defecto */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
