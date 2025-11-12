import { useState, useEffect } from 'react';
import { Car, LogIn, LogOut } from 'lucide-react';
import { http } from '../api/http';

export function VehicleManagementPanel({ onVehicleUpdate, onExitRegistered, placaSalidaInicial, onPlacaSalidaUsada }) {
  // Estados para entrada
  const [placaEntrada, setPlacaEntrada] = useState('');
  const [loadingEntrada, setLoadingEntrada] = useState(false);
  const [messageEntrada, setMessageEntrada] = useState(null);

  // Estados para salida
  const [placaSalida, setPlacaSalida] = useState('');
  const [loadingSalida, setLoadingSalida] = useState(false);
  const [messageSalida, setMessageSalida] = useState(null);
  const [ticketInfo, setTicketInfo] = useState(null);

  // Cuando se recibe una placa inicial desde VehiculosPage
  useEffect(() => {
    if (placaSalidaInicial) {
      setPlacaSalida(placaSalidaInicial);
      // Notificar que ya usamos la placa
      if (onPlacaSalidaUsada) {
        onPlacaSalidaUsada();
      }
    }
  }, [placaSalidaInicial, onPlacaSalidaUsada]);

  // Función para registrar entrada usando ticket_router
  const handleEntry = async (e) => {
    e.preventDefault();
    if (!placaEntrada.trim()) {
      setMessageEntrada({ type: 'error', text: 'Por favor ingrese una placa' });
      return;
    }

    setLoadingEntrada(true);
    setMessageEntrada(null);

    try {
      const response = await http.post('/tickets/entrada', {
        placa: placaEntrada.toUpperCase()
      });

      setMessageEntrada({ 
        type: 'success', 
        text: `✅ Vehículo ${placaEntrada.toUpperCase()} registrado - Ticket #${response.data.id}` 
      });
      setPlacaEntrada('');
      
      // Notificar al componente padre para actualizar la lista
      if (onVehicleUpdate) {
        onVehicleUpdate();
      }

      // Limpiar mensaje después de 5 segundos
      setTimeout(() => setMessageEntrada(null), 5000);
    } catch (error) {
      setMessageEntrada({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Error al registrar entrada' 
      });
    } finally {
      setLoadingEntrada(false);
    }
  };

  // Función para registrar salida usando ticket_router
  const handleExit = async (e) => {
    e.preventDefault();
    if (!placaSalida.trim()) {
      setMessageSalida({ type: 'error', text: 'Por favor ingrese una placa' });
      return;
    }

    setLoadingSalida(true);
    setMessageSalida(null);
    setTicketInfo(null);

    try {
      const response = await http.post('/tickets/salida', {
        placa: placaSalida.toUpperCase()
      });

      const ticket = response.data;
      setTicketInfo(ticket);
      
      setMessageSalida({ 
        type: 'success', 
        text: `✅ Salida registrada - Total a pagar: $${ticket.monto_total?.toLocaleString('es-CO') || 0}` 
      });
      
      // Agregar evento de salida a la actividad reciente
      if (onExitRegistered) {
        onExitRegistered(placaSalida.toUpperCase(), ticket);
      }
      
      setPlacaSalida('');
      
      // Notificar al componente padre para actualizar la lista
      if (onVehicleUpdate) {
        onVehicleUpdate();
      }

      // Limpiar solo el mensaje de éxito después de 5 segundos, pero mantener el ticketInfo visible
      setTimeout(() => {
        setMessageSalida(null);
      }, 5000);
    } catch (error) {
      setMessageSalida({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Error al registrar salida' 
      });
    } finally {
      setLoadingSalida(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center gap-2 mb-6">
        <Car className="w-6 h-6 text-blue-600" />
        <h2 className="text-xl font-bold text-gray-900">Gestión de Vehículos</h2>
      </div>

      {/* Dos paneles lado a lado */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Panel de Entrada (Izquierda) */}
        <div className="border border-gray-200 rounded-lg p-5 bg-green-50/30">
          <div className="flex items-center gap-2 mb-4">
            <LogIn className="w-5 h-5 text-green-600" />
            <h3 className="text-lg font-semibold text-gray-900">Registrar Entrada</h3>
          </div>

          <form onSubmit={handleEntry} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Placa del Vehículo
              </label>
              <input
                type="text"
                value={placaEntrada}
                onChange={(e) => setPlacaEntrada(e.target.value.toUpperCase())}
                placeholder="Ej: ABC123"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                disabled={loadingEntrada}
              />
            </div>
            <button
              type="submit"
              disabled={loadingEntrada}
              className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 rounded-lg transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <LogIn className="w-5 h-5" />
              {loadingEntrada ? 'Registrando...' : 'Registrar Entrada'}
            </button>
          </form>

          {/* Mensajes de entrada */}
          {messageEntrada && (
            <div
              className={`mt-4 p-3 rounded-lg text-sm ${
                messageEntrada.type === 'success'
                  ? 'bg-green-100 text-green-800 border border-green-200'
                  : 'bg-red-100 text-red-800 border border-red-200'
              }`}
            >
              {messageEntrada.text}
            </div>
          )}
        </div>

        {/* Panel de Salida (Derecha) */}
        <div className="border border-gray-200 rounded-lg p-5 bg-red-50/30">
          <div className="flex items-center gap-2 mb-4">
            <LogOut className="w-5 h-5 text-red-600" />
            <h3 className="text-lg font-semibold text-gray-900">Registrar Salida</h3>
          </div>

          <form onSubmit={handleExit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Placa del Vehículo
              </label>
              <input
                type="text"
                value={placaSalida}
                onChange={(e) => setPlacaSalida(e.target.value.toUpperCase())}
                placeholder="Ej: ABC123"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                disabled={loadingSalida}
              />
            </div>
            <button
              type="submit"
              disabled={loadingSalida}
              className="w-full bg-red-600 hover:bg-red-700 text-white font-medium py-3 rounded-lg transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <LogOut className="w-5 h-5" />
              {loadingSalida ? 'Procesando...' : 'Registrar Salida'}
            </button>
          </form>

          {/* Información del ticket de salida */}
          {ticketInfo && (
            <div className="mt-4 p-4 bg-white rounded-lg border border-gray-300">
              <h4 className="font-semibold text-gray-900 mb-3 text-sm">Resumen del Ticket</h4>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-600">Placa:</span>
                  <span className="font-mono font-bold text-gray-900 text-sm">
                    {ticketInfo.placa}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Entrada:</span>
                  <span className="font-medium text-gray-900">
                    {new Date(ticketInfo.hora_entrada).toLocaleString('es-CO')}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Salida:</span>
                  <span className="font-medium text-gray-900">
                    {new Date(ticketInfo.hora_salida).toLocaleString('es-CO')}
                  </span>
                </div>
                <div className="flex justify-between pt-2 border-t border-gray-200">
                  <span className="text-gray-900 font-semibold">Total:</span>
                  <span className="font-bold text-red-600 text-base">
                    ${ticketInfo.monto_total?.toLocaleString('es-CO') || 0}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Mensajes de salida */}
          {messageSalida && (
            <div
              className={`mt-4 p-3 rounded-lg text-sm ${
                messageSalida.type === 'success'
                  ? 'bg-green-100 text-green-800 border border-green-200'
                  : 'bg-red-100 text-red-800 border border-red-200'
              }`}
            >
              {messageSalida.text}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
