import {
  LayoutDashboard, Car, Activity, Database, LogOut, ChevronDown
} from 'lucide-react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';

const navItems = [
  { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { label: "Vehículos", path: "/dashboard/vehiculos", icon: Car },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const [openMenu, setOpenMenu] = useState(false);

  const handleLogout = async () => {
    const token = localStorage.getItem("token");

    if (!token) {
      localStorage.removeItem("token");
      navigate("/login");
      return;
    }

    try {
      // 🔹 Cerrar turno en el backend
      const res = await fetch("/api/turnos/cerrar", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (res.ok) {
        console.log("✅ Turno cerrado correctamente.");
      } else {
        const errorText = await res.text();
        console.warn("⚠️ No se pudo cerrar el turno:", errorText);
      }
    } catch (error) {
      console.error("❌ Error al cerrar el turno:", error);
    } finally {
      // 🔹 Limpiar token y redirigir
      localStorage.removeItem("token");
      localStorage.removeItem("usuario");
      localStorage.removeItem("turno");
      navigate("/login");
    }
  };

  useEffect(() => {
    const handleBeforeUnload = () => {
      const token = localStorage.getItem("token");
      if (token) {
        navigator.sendBeacon("https://nuvora/api/turnos/cerrar");
        localStorage.removeItem("token");
      }
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, []);

  return (
    <aside className="h-screen w-64 bg-white border-r flex flex-col relative">
      <div
        className="flex items-center justify-between px-6 py-5 border-b cursor-pointer relative"
        onClick={() => setOpenMenu(!openMenu)}
      >
        <div className="flex items-center">
          <div className="bg-blue-600 rounded-md w-10 h-10 flex items-center justify-center font-bold text-white text-xl">
            N
          </div>
          <div className="ml-3">
            <h1 className="font-bold text-lg text-gray-900">Nuvora</h1>
            <span className="text-xs text-gray-500">Gestión Inteligente</span>
          </div>
        </div>
        <ChevronDown className={`w-5 h-5 text-gray-600 transition-transform ${openMenu ? 'rotate-180' : ''}`} />
      </div>

      {openMenu && (
        <div className="absolute top-20 left-4 w-56 bg-white border rounded-lg shadow-lg z-50">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100"
          >
            <LogOut className="w-4 h-4" />
            Cerrar sesión
          </button>
        </div>
      )}

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
