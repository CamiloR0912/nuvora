import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { DollarSign, FileText, AlertCircle, CheckCircle } from "lucide-react";
import http from "../api/http";

export default function HacerCierrePage() {
  const navigate = useNavigate();
  const [observaciones, setObservaciones] = useState("");
  const [processing, setProcessing] = useState(false);

  const handleCrearCierre = async (e) => {
    e.preventDefault();

    if (!window.confirm("¿Estás seguro de crear el cierre de caja? Esta acción cerrará tu turno actual (si está abierto) y consolidará todos los turnos pendientes.")) {
      return;
    }

    setProcessing(true);
    try {
      const res = await http.post("/cierres/", {
        observaciones: observaciones.trim() || null
      });

      // Actualizar el token (sin turno_id)
      if (res.data.access_token) {
        localStorage.setItem("token", res.data.access_token);
        console.log("✅ Token actualizado después del cierre");
      }

      // Limpiar el turno del localStorage
      localStorage.removeItem("turno");

      alert(`✅ Cierre de caja creado exitosamente!\n\nCierre ID: ${res.data.id}\nTotal recaudado: $${res.data.total_recaudado?.toLocaleString('es-CO') || 0}\nVehículos: ${res.data.total_vehiculos || 0}`);
      
      // Redirigir a iniciar turno
      navigate("/start-shift", { replace: true });
    } catch (error) {
      console.error("Error creando cierre:", error);
      const errorMsg = error.response?.data?.detail || error.message || "Error desconocido";
      alert("❌ Error al crear cierre: " + errorMsg);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Hacer Cierre de Caja</h1>
        <p className="text-gray-600 mt-2">Consolida todos tus turnos pendientes en un solo cierre</p>
      </div>

      <div className="bg-white rounded-xl shadow-lg border-2 border-blue-200 p-8">
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
          <div className="flex items-start">
            <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 mr-3" />
            <div>
              <h3 className="font-semibold text-blue-900 mb-1">¿Qué hace el cierre de caja?</h3>
              <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
                <li>Cierra tu turno actual (si tienes uno abierto)</li>
                <li>Consolida TODOS los turnos cerrados que aún no han sido incluidos en un cierre</li>
                <li>Calcula el total recaudado y vehículos atendidos</li>
                <li>Te permite iniciar un nuevo turno después</li>
              </ul>
            </div>
          </div>
        </div>

        <form onSubmit={handleCrearCierre} className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              <FileText className="w-4 h-4 inline mr-1" />
              Observaciones (Opcional)
            </label>
            <textarea
              value={observaciones}
              onChange={(e) => setObservaciones(e.target.value)}
              placeholder="Ej: Cierre de fin de día, turno nocturno..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows={4}
            />
            <p className="text-xs text-gray-500 mt-1">
              Puedes agregar notas sobre este cierre (opcional)
            </p>
          </div>

          <div className="flex gap-4">
            <button
              type="button"
              onClick={() => navigate("/dashboard")}
              className="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-semibold"
              disabled={processing}
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={processing}
              className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {processing ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Procesando...
                </>
              ) : (
                <>
                  <CheckCircle className="w-5 h-5" />
                  Crear Cierre de Caja
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
