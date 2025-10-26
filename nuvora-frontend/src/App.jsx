import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import Detection from './pages/Detection';
import DashboardLayout from './layouts/DashboardLayout';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Login */}
        <Route path="/" element={<LoginPage />} />

        {/* Dashboard con Sidebar */}
        <Route path="/dashboard" element={<DashboardLayout />}>
          <Route index element={<HomePage />} /> {/* Página principal */}
          <Route path="detection" element={<Detection />} /> {/* Página de detección */}
        </Route>

        {/* Redirección por defecto */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
