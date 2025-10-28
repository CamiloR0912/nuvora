import Sidebar from '../components/Sidebar';
import { Outlet } from 'react-router-dom';

export default function DashboardLayout() {
  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Barra lateral */}
      <Sidebar />

      {/* Contenido principal */}
      <main className="flex-1 p-6 overflow-y-auto">
        <Outlet /> {/* 👈 Aquí React Router inyecta HomePage, Detection, etc */}
      </main>
    </div>
  );
}
