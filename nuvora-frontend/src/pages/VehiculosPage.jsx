import React, { useEffect, useState } from "react";
import { Car, Clock, Plus, LogOut, X, Search } from "lucide-react";
import { getVehiculosActivos, registrarEntrada, registrarSalida } from "../api/vehiculosApi";
import { useNavigate } from "react-router-dom";

function formatDuration(fecha_entrada) {
  const entryTime = new Date(fecha_entrada);
  const now = new Date();
  const diffMs = now - entryTime;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours > 0) {
    return `${diffHours}h ${diffMins % 60}m`;
  }
  return `${diffMins}m`;
}

// Modal reutilizable
function Modal({ isOpen, onClose, title, children }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-lg w-full max-w-md p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
        >
          <X className="w-5 h-5" />
        </button>
        <h3 className="text-xl font-bold text-gray-900 mb-4">{title}</h3>
        {children}
      </div>
    </div>
  );
}

export default function VehiculosPage() {
  const navigate = useNavigate();
  const [vehiculos, setVehiculos] = useState([]);
  const [vehiculosFiltrados, setVehiculosFiltrados] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Estados para modal de entrada
  const [showEntradaModal, setShowEntradaModal] = useState(false);
  const [placaEntrada, setPlacaEntrada] = useState("");
  const [loadingEntrada, setLoadingEntrada] = useState(false);
  const [errorEntrada, setErrorEntrada] = useState("");

  // Estados para modal de salida
  const [showSalidaModal, setShowSalidaModal] = useState(false);
  const [placaSalida, setPlacaSalida] = useState("");
  const [loadingSalida, setLoadingSalida] = useState(false);
  const [errorSalida, setErrorSalida] = useState("");

  useEffect(() => {
    cargarVehiculos();
  }, []);

  // Filtrar vehículos cuando cambia el término de búsqueda
  useEffect(() => {
    if (searchTerm.trim() === "") {
      setVehiculosFiltrados(vehiculos);
    } else {
      const filtered = vehiculos.filter((vehiculo) =>
        vehiculo.placa.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setVehiculosFiltrados(filtered);
    }
  }, [searchTerm, vehiculos]);

  const cargarVehiculos = () => {
    setLoading(true);
    getVehiculosActivos()
      .then((res) => {
        if (Array.isArray(res.data)) {
          // Mapear la respuesta de tickets a formato esperado por el componente
          const vehiculosFormateados = res.data.map(ticket => ({
            id: ticket.id,
            placa: ticket.placa,
            fecha_entrada: ticket.hora_entrada, // Mapear hora_entrada a fecha_entrada
            espacio: null, // No hay campo de espacio en tickets
            usuario_nombre: ticket.usuario_entrada_nombre // Nombre del usuario que registró la entrada
          }));
          
          // Ordenar del más reciente al más antiguo
          const vehiculosOrdenados = vehiculosFormateados.sort((a, b) => 
            new Date(b.fecha_entrada) - new Date(a.fecha_entrada)
          );
          
          setVehiculos(vehiculosOrdenados);
          setVehiculosFiltrados(vehiculosOrdenados);
        } else {
          setVehiculos([]);
          setVehiculosFiltrados([]);
        }
        setError("");
      })
      .catch((err) => {
        setVehiculos([]);
        setVehiculosFiltrados([]);
        const errorMsg = err.response?.data?.detail || "No se pudieron obtener los vehículos.";
        setError(errorMsg);
      })
      .finally(() => setLoading(false));
  };

  // Manejar registro de entrada
  const handleRegistrarEntrada = async (e) => {
    e.preventDefault();
    setErrorEntrada("");
    
    const placa = placaEntrada.trim().toUpperCase();
    if (!placa) {
      setErrorEntrada("La placa es obligatoria");
      return;
    }

    setLoadingEntrada(true);
    try {
      await registrarEntrada({ placa });
      setShowEntradaModal(false);
      setPlacaEntrada("");
      cargarVehiculos(); // Recargar lista
    } catch (err) {
      const msg = err.response?.data?.detail || "Error al registrar entrada";
      setErrorEntrada(msg);
    } finally {
      setLoadingEntrada(false);
    }
  };

  // Manejar registro de salida
  const handleRegistrarSalida = async (e) => {
  e.preventDefault();
  setErrorSalida("");

  const placa = placaSalida.trim().toUpperCase();
  if (!placa) {
    setErrorSalida("La placa es obligatoria");
    return;
  }

  // El backend registra la hora automáticamente
  const payload = { placa };

  console.log("📤 [VehiculosPage] Enviando payload de salida:", payload);

  setLoadingSalida(true);
  try {
    const res = await registrarSalida(payload);
    console.log("✅ [VehiculosPage] Respuesta registrarSalida:", res.data);
    setShowSalidaModal(false);
    setPlacaSalida("");
    cargarVehiculos(); // Recargar lista
  } catch (err) {
    console.error("❌ [VehiculosPage] Error registrarSalida:", err);
    console.error("   response:", err.response);
    const msg =
      err.response?.data?.detail ||
      err.response?.data ||
      `Error ${err.response?.status || ""}`;
    setErrorSalida(msg || "Error al registrar salida");
  } finally {
    setLoadingSalida(false);
  }
};

  // Registrar salida directa desde el botón del vehículo
  const handleSalidaDirecta = (placa) => {
    // Navegar a HomePage con la placa en el state
    navigate('/dashboard', { state: { placaSalida: placa } });
  };

  return (
    <div className="max-w-3xl mx-auto py-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <Car className="w-7 h-7 text-blue-600 mr-3" />
          <h2 className="text-2xl font-bold text-gray-900">Vehículos en el Parqueadero</h2>
        </div>
        
        {/* Botones de acción */}
        <div className="flex gap-3">
          <button
            onClick={() => setShowEntradaModal(true)}
            className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
          >
            <Plus className="w-4 h-4" />
            Registrar Entrada
          </button>
          <button
            onClick={() => setShowSalidaModal(true)}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            <LogOut className="w-4 h-4" />
            Registrar Salida
          </button>
        </div>
      </div>

      {/* Barra de búsqueda */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Buscar por placa..."
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm("")}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
        {searchTerm && (
          <p className="mt-2 text-sm text-gray-600">
            {vehiculosFiltrados.length === 0 
              ? "No se encontraron vehículos con esa placa"
              : `${vehiculosFiltrados.length} vehículo${vehiculosFiltrados.length !== 1 ? 's' : ''} encontrado${vehiculosFiltrados.length !== 1 ? 's' : ''}`
            }
          </p>
        )}
      </div>

      {loading ? (
        <div className="text-center py-8">Cargando...</div>
      ) : error ? (
        <div className="bg-red-100 text-red-800 rounded-xl shadow p-8 text-center text-lg">
          {error}
        </div>
      ) : vehiculosFiltrados.length === 0 ? (
        <div className="bg-white rounded-xl shadow p-8 text-center text-gray-500 text-lg">
          {searchTerm 
            ? `No se encontraron vehículos con la placa "${searchTerm}"`
            : "No hay vehículos actualmente en el parqueadero."
          }
        </div>
      ) : (
        <ul className="space-y-4">
          {vehiculosFiltrados.map((v) => (
            <li
              key={v.id}
              className="flex items-center justify-between bg-white p-5 rounded-xl shadow-sm border border-slate-100 hover:shadow transition"
            >
              <div className="flex items-center gap-4">
                <div className="bg-blue-100 p-3 rounded-lg">
                  <Car className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <div className="text-lg font-semibold text-gray-800">{v.placa}</div>
                  <div className="text-xs text-gray-500">
                    Ingreso:{" "}
                    <span className="font-medium">
                      {new Date(v.fecha_entrada).toLocaleString()}
                    </span>
                  </div>
                  {v.usuario_nombre && (
                    <div className="text-xs text-gray-500">
                      Registrado por: <span className="font-medium">{v.usuario_nombre}</span>
                    </div>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex items-center text-gray-600 text-sm">
                  <Clock className="w-4 h-4 mr-2" />
                  <span className="font-medium">{formatDuration(v.fecha_entrada)}</span>
                </div>
                <button
                  onClick={() => handleSalidaDirecta(v.placa)}
                  className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition text-sm"
                  title="Registrar salida"
                >
                  <LogOut className="w-4 h-4" />
                  Salida
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      {/* Modal de Entrada */}
      <Modal
        isOpen={showEntradaModal}
        onClose={() => {
          setShowEntradaModal(false);
          setPlacaEntrada("");
          setErrorEntrada("");
        }}
        title="Registrar Entrada Manual"
      >
        <form onSubmit={handleRegistrarEntrada} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Placa del vehículo *
            </label>
            <input
              type="text"
              value={placaEntrada}
              onChange={(e) => setPlacaEntrada(e.target.value.toUpperCase())}
              placeholder="ABC123"
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none font-mono tracking-widest"
              maxLength={10}
              required
            />
          </div>

          {errorEntrada && (
            <div className="text-red-600 text-sm">{errorEntrada}</div>
          )}

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={() => {
                setShowEntradaModal(false);
                setPlacaEntrada("");
                setErrorEntrada("");
              }}
              className="flex-1 bg-gray-200 text-gray-700 py-2 rounded-lg hover:bg-gray-300 transition"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loadingEntrada}
              className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition disabled:opacity-60"
            >
              {loadingEntrada ? "Registrando..." : "Registrar Entrada"}
            </button>
          </div>
        </form>
      </Modal>

      {/* Modal de Salida */}
      <Modal
        isOpen={showSalidaModal}
        onClose={() => {
          setShowSalidaModal(false);
          setPlacaSalida("");
          setErrorSalida("");
        }}
        title="Registrar Salida Manual"
      >
        <form onSubmit={handleRegistrarSalida} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Placa del vehículo *
            </label>
            <input
              type="text"
              value={placaSalida}
              onChange={(e) => setPlacaSalida(e.target.value.toUpperCase())}
              placeholder="ABC123"
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none font-mono tracking-widest"
              maxLength={10}
              required
            />
            <p className="text-xs text-gray-500 mt-2">
              La hora de salida se registrará automáticamente
            </p>
          </div>

          {errorSalida && (
            <div className="text-red-600 text-sm">{errorSalida}</div>
          )}

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={() => {
                setShowSalidaModal(false);
                setPlacaSalida("");
                setErrorSalida("");
              }}
              className="flex-1 bg-gray-200 text-gray-700 py-2 rounded-lg hover:bg-gray-300 transition"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loadingSalida}
              className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-60"
            >
              {loadingSalida ? "Registrando..." : "Registrar Salida"}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
