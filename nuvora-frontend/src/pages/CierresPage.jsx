import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { DollarSign, FileText, Calendar } from "lucide-react";
import http from "../api/http";
import { jwtDecode } from 'jwt-decode';

export default function CierresPage() {
  const navigate = useNavigate();
  const [cierres, setCierres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    // Verificar que el usuario sea admin antes de cargar cierres
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const decoded = jwtDecode(token);
        // El rol puede estar en decoded.rol O en decoded.usuario.rol
        const userRole = decoded.rol || decoded.usuario?.rol || 'user';
        
        if (userRole !== 'admin') {
          setError('No tienes permisos para ver esta página');
          navigate('/dashboard');
          return;
        }
      } catch (error) {
        console.error('Error decoding token:', error);
        navigate('/dashboard');
        return;
      }
    }
    
    loadCierres();
  }, [navigate]);

  const loadCierres = async () => {
    setLoading(true);
    try {
      const res = await http.get("/cierres/");
      setCierres(res.data);
      setError("");
    } catch (err) {
      console.error("Error cargando cierres:", err);
      const errorMsg = err.response?.data?.detail || "No se pudieron cargar los cierres";
      setError(errorMsg);
      setCierres([]);
    } finally {
      setLoading(false);
    }
  };  const formatCurrency = (value) => {
    return new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: "COP",
      minimumFractionDigits: 0,
    }).format(value || 0);
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleString("es-CO", {
      dateStyle: "medium",
      timeStyle: "short",
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Cargando cierres...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Historial de Cierres</h1>
          <p className="text-gray-600 mt-2">Listado completo de todos los cierres de caja</p>
        </div>
      </div>

      {error ? (
        <div className="bg-red-100 text-red-800 rounded-xl shadow p-8 text-center">
          <p className="text-lg font-semibold">{error}</p>
        </div>
      ) : cierres.length === 0 ? (
        <div className="bg-white rounded-xl shadow p-8 text-center text-gray-500">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-lg">No hay cierres registrados</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cierres.map((cierre) => (
            <div
              key={cierre.id}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-900">Cierre #{cierre.id}</h3>
                <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold">
                  COMPLETADO
                </span>
              </div>

              <div className="space-y-3">
                <div className="bg-blue-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600 mb-1">Turno Asociado</p>
                  <p className="text-lg font-bold text-blue-700">Turno #{cierre.turno_id}</p>
                </div>

                <div className="flex items-center gap-2">
                  <DollarSign className="w-4 h-4 text-green-600" />
                  <div className="flex-1">
                    <p className="text-xs text-gray-600">Total Recaudado</p>
                    <p className="text-lg font-bold text-green-700">
                      {formatCurrency(cierre.total_recaudado)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-purple-600" />
                  <div className="flex-1">
                    <p className="text-xs text-gray-600">Vehículos</p>
                    <p className="text-lg font-bold text-purple-700">{cierre.total_vehiculos}</p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-blue-600" />
                  <div className="flex-1">
                    <p className="text-xs text-gray-600">Fecha de Cierre</p>
                    <p className="text-sm font-medium text-gray-900">
                      {formatDateTime(cierre.fecha_cierre)}
                    </p>
                  </div>
                </div>

                {cierre.observaciones && (
                  <div className="bg-yellow-50 rounded-lg p-3 border-l-4 border-yellow-400">
                    <p className="text-xs text-gray-600 mb-1">Observaciones:</p>
                    <p className="text-sm text-gray-900">{cierre.observaciones}</p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
