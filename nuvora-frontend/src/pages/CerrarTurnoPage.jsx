import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Clock, DollarSign, Users, AlertCircle, CheckCircle } from "lucide-react";
import http from "../api/http";

export default function CerrarTurnoPage() {
  const navigate = useNavigate();
  const [turnoActual, setTurnoActual] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    loadTurnoActual();
  }, []);

  const loadTurnoActual = async () => {
    try {
      const res = await http.get("/turnos/actual");
      setTurnoActual(res.data);
    } catch (error) {
      console.error("Error cargando turno actual:", error);
      setTurnoActual(null);
    } finally {
      setLoading(false);
    }
  };

  const handleCerrarTurno = async () => {
    if (!window.confirm("¿Estás seguro de cerrar tu turno actual? Esta acción no se puede deshacer.")) {
      return;
    }

    setProcessing(true);
    try {
      const res = await http.post("/turnos/cerrar");
      
      // Actualizar el token (sin turno_id)
      if (res.data.access_token) {
        localStorage.setItem("token", res.data.access_token);
        console.log("✅ Token actualizado (sin turno_id)");
      }

      // Limpiar el turno del localStorage
      localStorage.removeItem("turno");

      alert(`✅ Turno cerrado exitosamente!\n\nTotal recaudado: $${res.data.monto_total?.toLocaleString() || 0}\nVehículos atendidos: ${res.data.total_vehiculos || 0}`);
      
      // Redirigir a iniciar turno
      navigate("/start-shift", { replace: true });
    } catch (error) {
      console.error("Error cerrando turno:", error);
      alert("❌ Error al cerrar turno: " + (error.response?.data?.detail || error.message));
    } finally {
      setProcessing(false);
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
      dateStyle: "medium",
      timeStyle: "short",
    });
  };

  const calcularDuracion = () => {
    if (!turnoActual?.fecha_inicio) return "N/A";
    const inicio = new Date(turnoActual.fecha_inicio);
    const ahora = new Date();
    const diff = ahora - inicio;
    const horas = Math.floor(diff / 1000 / 60 / 60);
    const minutos = Math.floor((diff / 1000 / 60) % 60);
    return `${horas}h ${minutos}m`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">Cargando información del turno...</div>
      </div>
    );
  }

  if (!turnoActual) {
    return (
      <div className="max-w-2xl mx-auto py-12 px-4">
        <div className="bg-yellow-50 border-2 border-yellow-200 rounded-xl p-8 text-center">
          <AlertCircle className="w-16 h-16 text-yellow-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No tienes un turno abierto</h2>
          <p className="text-gray-600 mb-6">
            Debes iniciar un turno antes de poder cerrarlo.
          </p>
          <button
            onClick={() => navigate("/dashboard/iniciar-turno")}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition font-semibold"
          >
            Iniciar Turno
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Cerrar Mi Turno</h1>
        <p className="text-gray-600 mt-2">Revisa el resumen antes de cerrar tu turno</p>
      </div>

      <div className="bg-white rounded-xl shadow-lg border-2 border-blue-200 p-8 mb-6">
        <div className="flex items-center justify-between mb-6 pb-6 border-b">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Turno #{turnoActual.id}</h2>
            <p className="text-gray-600">Turno actualmente abierto</p>
          </div>
          <span className="px-4 py-2 bg-green-100 text-green-700 rounded-full font-semibold">
            ACTIVO
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center gap-3 mb-2">
              <Clock className="w-5 h-5 text-blue-600" />
              <span className="text-sm font-semibold text-gray-700">Inicio del Turno</span>
            </div>
            <p className="text-lg font-bold text-gray-900">{formatDateTime(turnoActual.fecha_inicio)}</p>
          </div>

          <div className="bg-purple-50 rounded-lg p-4">
            <div className="flex items-center gap-3 mb-2">
              <Clock className="w-5 h-5 text-purple-600" />
              <span className="text-sm font-semibold text-gray-700">Duración</span>
            </div>
            <p className="text-lg font-bold text-gray-900">{calcularDuracion()}</p>
          </div>

          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-center gap-3 mb-2">
              <DollarSign className="w-5 h-5 text-green-600" />
              <span className="text-sm font-semibold text-gray-700">Monto Inicial</span>
            </div>
            <p className="text-lg font-bold text-gray-900">{formatCurrency(turnoActual.monto_inicial)}</p>
          </div>

          <div className="bg-emerald-50 rounded-lg p-4 border-2 border-emerald-200">
            <div className="flex items-center gap-3 mb-2">
              <DollarSign className="w-5 h-5 text-emerald-600" />
              <span className="text-sm font-semibold text-gray-700">Ganancias Actuales</span>
            </div>
            <p className="text-2xl font-bold text-emerald-700">{formatCurrency(turnoActual.monto_total || 0)}</p>
            {turnoActual.total_vehiculos > 0 && (
              <p className="text-xs text-emerald-600 mt-1">
                {turnoActual.total_vehiculos} vehículo{turnoActual.total_vehiculos !== 1 ? 's' : ''} cerrado{turnoActual.total_vehiculos !== 1 ? 's' : ''}
              </p>
            )}
          </div>
        </div>

        {turnoActual.observaciones && (
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <p className="text-sm font-semibold text-gray-700 mb-1">Observaciones:</p>
            <p className="text-gray-900">{turnoActual.observaciones}</p>
          </div>
        )}

        <div className="flex gap-4">
          <button
            onClick={() => navigate("/dashboard")}
            className="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-semibold"
            disabled={processing}
          >
            Cancelar
          </button>
          <button
            onClick={handleCerrarTurno}
            disabled={processing}
            className="flex-1 px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {processing ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Cerrando...
              </>
            ) : (
              <>
                <CheckCircle className="w-5 h-5" />
                Cerrar Turno
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
