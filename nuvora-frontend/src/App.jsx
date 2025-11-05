import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import VehiculosPage from './pages/VehiculosPage';
import ActividadPage from './pages/ActividadPage';
import BaseDatosPage from './pages/BaseDatosPage';
import DashboardLayout from './layouts/DashboardLayout';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Login */}
        <Route path="/" element={<LoginPage />} />

        {/* Dashboard con Sidebar */}
        <Route path="/dashboard" element={<DashboardLayout />}>
          <Route index element={<HomePage />} />
          <Route path="vehiculos" element={<VehiculosPage />} />
          <Route path="actividad" element={<ActividadPage />} />
          <Route path="bd" element={<BaseDatosPage />} /> {/* Nueva ruta */}
        </Route>

        {/* Redirección por defecto */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
