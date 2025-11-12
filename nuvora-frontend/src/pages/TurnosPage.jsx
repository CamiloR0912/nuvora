import React, { useState, useEffect } from "react";
import { Clock, DollarSign, Users, CheckCircle, XCircle, Calendar } from "lucide-react";
import http from "../api/http";

export default function TurnosPage() {
  const [turnos, setTurnos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userRole, setUserRole] = useState(null);

  useEffect(() => {
    loadTurnos();
    checkUserRole();
  }, []);

  const checkUserRole = () => {
    const usuario = JSON.parse(localStorage.getItem("usuario") || "{}");
    setUserRole(usuario.rol);
  };

  const loadTurnos = async () => {
    try {
      const usuario = JSON.parse(localStorage.getItem("usuario") || "{}");
      const endpoint = usuario.rol === "admin" ? "/turnos/todos" : "/turnos/";
      const res = await http.get(endpoint);
      setTurnos(res.data || []);
    } catch (error) {
      console.error("Error cargando turnos:", error);
      setTurnos([]);
    } finally {
      setLoading(false);
    }
  };

  const cerrarTurno = async (turnoId) => {
    if (!window.confirm("¿Estás seguro de cerrar este turno?")) return;

    try {
      await http.post(`/turnos/${turnoId}/cerrar`);
      alert("Turno cerrado exitosamente");
      loadTurnos();
    } catch (error) {
      console.error("Error cerrando turno:", error);
      alert("Error al cerrar turno: " + (error.response?.data?.detail || error.message));
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: "COP",
      minimumFractionDigits: 0,
    }).format(value || 0);
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleString("es-CO", {
      dateStyle: "short",
      timeStyle: "short",
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">Cargando turnos...</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Gestión de Turnos</h1>
        <p className="text-gray-600 mt-2">
          {userRole === "admin" 
            ? "Vista de todos los turnos del sistema" 
            : "Historial de tus turnos"}
        </p>
      </div>

      {turnos.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border p-12 text-center">
          <Clock className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No hay turnos registrados</h3>
          <p className="text-gray-500">Inicia un nuevo turno para comenzar a trabajar</p>
        </div>
      ) : (
        <div className="grid gap-6">
          {turnos.map((turno) => (
            <div
              key={turno.id}
              className={`bg-white rounded-xl shadow-sm border-2 p-6 transition-all hover:shadow-md ${
                turno.estado === "abierto" 
                  ? "border-green-200 bg-green-50" 
                  : turno.incluido_en_cierre 
                    ? "border-gray-200" 
                    : "border-blue-200 bg-blue-50"
              }`}
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <div className="flex items-center gap-3">
                    <h3 className="text-xl font-bold text-gray-900">Turno #{turno.id}</h3>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        turno.estado === "abierto"
                          ? "bg-green-100 text-green-700"
                          : "bg-gray-100 text-gray-700"
                      }`}
                    >
                      {turno.estado === "abierto" ? "ACTIVO" : "CERRADO"}
                    </span>
                    {turno.estado === "cerrado" && (
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          turno.incluido_en_cierre
                            ? "bg-purple-100 text-purple-700"
                            : "bg-blue-100 text-blue-700"
                        }`}
                      >
                        {turno.incluido_en_cierre ? "EN CIERRE" : "PENDIENTE CIERRE"}
                      </span>
                    )}
                  </div>
                  {turno.observaciones && (
                    <p className="text-sm text-gray-600 mt-2">{turno.observaciones}</p>
                  )}
                </div>

                {turno.estado === "abierto" && userRole === "admin" && (
                  <button
                    onClick={() => cerrarTurno(turno.id)}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition flex items-center gap-2"
                  >
                    <XCircle className="w-4 h-4" />
                    Cerrar Turno
                  </button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="flex items-center gap-3">
                  <div className="bg-blue-100 p-3 rounded-lg">
                    <Calendar className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Inicio</p>
                    <p className="font-semibold text-gray-900">{formatDateTime(turno.fecha_inicio)}</p>
                  </div>
                </div>

                {turno.fecha_fin && (
                  <div className="flex items-center gap-3">
                    <div className="bg-orange-100 p-3 rounded-lg">
                      <Calendar className="w-5 h-5 text-orange-600" />
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Fin</p>
                      <p className="font-semibold text-gray-900">{formatDateTime(turno.fecha_fin)}</p>
                    </div>
                  </div>
                )}

                <div className="flex items-center gap-3">
                  <div className="bg-green-100 p-3 rounded-lg">
                    <DollarSign className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Inicial</p>
                    <p className="font-semibold text-gray-900">{formatCurrency(turno.monto_inicial)}</p>
                  </div>
                </div>

                {turno.monto_total !== null && turno.monto_total !== undefined && (
                  <div className="flex items-center gap-3">
                    <div className="bg-purple-100 p-3 rounded-lg">
                      <DollarSign className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Recaudado</p>
                      <p className="font-bold text-lg text-purple-900">{formatCurrency(turno.monto_total)}</p>
                    </div>
                  </div>
                )}

                {turno.total_vehiculos > 0 && (
                  <div className="flex items-center gap-3">
                    <div className="bg-indigo-100 p-3 rounded-lg">
                      <Users className="w-5 h-5 text-indigo-600" />
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Vehículos</p>
                      <p className="font-semibold text-gray-900">{turno.total_vehiculos}</p>
                    </div>
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
