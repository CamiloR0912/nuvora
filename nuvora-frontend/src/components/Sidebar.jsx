import {
  LayoutDashboard, Camera, Car, BarChart, Mic, Activity, Database, Settings
} from 'lucide-react';
import { NavLink } from 'react-router-dom';

const navItems = [
  { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { label: "Vehículos", path: "/dashboard/vehiculos", icon: Car },
  { label: "Actividad", path: "/dashboard/actividad", icon: Activity },
  { label: "Base de Datos", path: "/dashboard/bd", icon: Database },
];

export default function Sidebar() {
  return (
    <aside className="h-screen w-64 bg-white border-r flex flex-col">
      <div className="flex items-center px-6 py-5 border-b">
        <div className="bg-blue-600 rounded-md w-10 h-10 flex items-center justify-center font-bold text-white text-xl">N</div>
        <div className="ml-3">
          <h1 className="font-bold text-lg text-gray-900">Nuvora</h1>
          <span className="text-xs text-gray-500">Gestión Inteligente</span>
        </div>
      </div>
      <nav className="flex-1 px-3 py-6">
        <ul className="space-y-2">
          {navItems.map(({ label, path, icon: Icon }) => (
            <li key={label}>
              <NavLink
                to={path}
                className={({ isActive }) =>
                  `flex items-center px-4 py-2 rounded-lg transition 
                   ${isActive ? 'bg-slate-100 text-blue-700 font-semibold' : 'text-gray-700 hover:bg-slate-50'}`
                }
                end
              >
                <Icon className="w-5 h-5 mr-3" />
                <span className="truncate">{label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      <div className="px-6 py-5 bg-slate-50 border-t">
        <div className="flex items-center space-x-2">
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-sm text-gray-700">Operativo</span>
        </div>
        <div className="text-xs text-gray-500 mt-1">Estado del Sistema</div>
      </div>
    </aside>
  );
}
