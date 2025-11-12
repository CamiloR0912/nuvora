import { useState, useEffect, useCallback } from 'react';
import { StatCard } from '../components/StatCard';
import { ParkingSpaceGrid } from '../components/ParkingSpaceGrid';
import { VehicleList } from '../components/VehicleList';
import { RecentActivity } from '../components/RecentActivity';
import Detection from '../components/Detection';
import { Car, ParkingCircle, Clock, Mic, Pencil } from 'lucide-react';
import { VoiceControlPanel } from '../components/VoiceControlPanel';
import { useSSE } from '../api/useSSE';
// import axios from 'axios'; // eliminado: usamos instancia http
import { http } from '../api/http';

// Simulación de cupos (sigue igual, puedes cambiar por tu backend real luego)
const mockParkingSpaces = [
  { id: 1, floor: 1, zone: 'A', space_number: 'A1', is_occupied: false },
  { id: 2, floor: 1, zone: 'A', space_number: 'A2', is_occupied: true },
  { id: 3, floor: 1, zone: 'B', space_number: 'B1', is_occupied: false },
  { id: 4, floor: 2, zone: 'C', space_number: 'C1', is_occupied: true },
  { id: 5, floor: 2, zone: 'C', space_number: 'C2', is_occupied: false },
];

export default function HomePage() {
  const [parkingSpaces, setParkingSpaces] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalCupos, setTotalCupos] = useState(0);
  const [editing, setEditing] = useState(false);
  const [newTotalCupos, setNewTotalCupos] = useState('');
  const [savingTotal, setSavingTotal] = useState(false);
  
  // Estados para detecciones en tiempo real
  const [lastDetection, setLastDetection] = useState(null);
  const [recentDetections, setRecentDetections] = useState([]);

  // Obtener token del localStorage
  const token = localStorage.getItem('token');

  // Callback para manejar mensajes SSE
  const handleSSEMessage = useCallback((data) => {
    if (data.event_type === 'vehicle_detected') {
      const detection = {
        placa: data.placa,
        timestamp: data.timestamp || data.hora_entrada, // Usar timestamp del SSE
        vehicle_type: data.vehicle_type || 'car'
      };
      
      // Actualizar última detección
      setLastDetection(detection);
      
      // Agregar a detecciones recientes (máximo 5)
      setRecentDetections(prev => [detection, ...prev].slice(0, 5));
      
      // Opcional: Reproducir sonido de notificación
      // const audio = new Audio('/notification.mp3');
      // audio.play();
      
      console.log('🚗 Vehículo detectado:', detection);
    }
  }, []);

  // Conectar a eventos SSE
  const { isConnected, error } = useSSE(
    'http://localhost:8000/api/events/stream',
    handleSSEMessage,
    token
  );

  useEffect(() => {
    // Cargar cupos simulados y datos reales de vehículos/eventos
    Promise.all([
      Promise.resolve(mockParkingSpaces),
      http.get('/tickets/abiertos'),
      http.get('/tickets/'),
      http.get('/configuracion/')
    ])
      .then(([mockSpaces, activosRes, historialRes, configuracionRes]) => {
        setParkingSpaces(mockSpaces);

        // Mapea vehículos activos según API real (tickets abiertos)
        setVehicles(
          activosRes.data.map(v => ({
            id: v.id,
            license_plate: v.placa,
            entry_time: new Date(v.hora_entrada),
            parking_spaces: { space_number: v.espacio || 'Desconocido' }
          }))
        );

        // Entradas
        const entradas = activosRes.data.map(v => ({
          id: `entrada-${v.id}`,
          event_type: 'entry',
          event_data: {
            description: `Vehículo ${v.placa} ingresó al parqueadero`
          },
          created_at: v.hora_entrada
        }));

        // Salidas
        const salidas = historialRes.data.map(v => ({
          id: `salida-${v.id}`,
          event_type: 'exit',
          event_data: {
            description: `Vehículo ${v.placa} salió del parqueadero`
          },
          created_at: v.hora_salida
        }));

        // Configuración
        setTotalCupos(configuracionRes?.data?.total_cupos ?? 0);
        setNewTotalCupos(String(configuracionRes?.data?.total_cupos ?? 0));

        // Combinar y mostrar solo las 3 actividades más recientes
        const ambos = [...entradas, ...salidas]
          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
          .slice(0, 3);

        setEvents(ambos);
        setLoading(false);
      })
      .catch(() => {
        setVehicles([]);
        setEvents([]);
        setLoading(false);
      });
  }, []);

  const occupiedSpaces = vehicles.length; // número de vehículos activos
  const availableSpaces = Math.max((totalCupos || 0) - occupiedSpaces, 0);

  async function saveTotalCupos() {
    try {
      setSavingTotal(true);
      const parsed = parseInt(newTotalCupos, 10);
      if (isNaN(parsed) || parsed < 0) return;
      const res = await http.put('/configuracion/', { total_cupos: parsed });
      setTotalCupos(res?.data?.total_cupos ?? parsed);
      setEditing(false);
    } catch (e) {
      console.error('Error actualizando total de cupos', e);
    } finally {
      setSavingTotal(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Cargando Nuvora...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Indicador de conexión SSE */}
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          ⚠️ Error de conexión con eventos en tiempo real: {error}
        </div>
      )}
      
      {/* Tarjetas de estadísticas principales */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="relative">
          <StatCard title="Total de Cupos" value={totalCupos} icon={ParkingCircle} subtitle="Capacidad total" />
          <div className="absolute top-3 right-3">
            {!editing ? (
              <button
                className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                onClick={() => setEditing(true)}
              >Editar</button>
            ) : (
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  min="0"
                  className="w-20 px-2 py-1 border rounded text-sm"
                  value={newTotalCupos}
                  onChange={(e) => setNewTotalCupos(e.target.value)}
                />
                <button
                  className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                  onClick={saveTotalCupos}
                  disabled={savingTotal}
                >Guardar</button>
                <button
                  className="px-3 py-1 text-xs bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
                  onClick={() => { setEditing(false); setNewTotalCupos(String(totalCupos)); }}
                >Cancelar</button>
              </div>
            )}
          </div>
        </div>
        <StatCard title="Cupos Ocupados" value={occupiedSpaces} icon={Car} subtitle={`${totalCupos ? Math.round((occupiedSpaces / totalCupos) * 100) : 0}% ocupación`} />
        <StatCard title="Cupos Disponibles" value={availableSpaces} icon={ParkingCircle} subtitle="Listos para usar" />
      </div>

      {/* Aquí va el Detection, ocupa todo el ancho izquierdo del grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2">
          <Detection 
            lastDetection={lastDetection} 
            recentDetections={recentDetections}
          />
        </div>
        <div className="flex flex-col space-y-6">
          <RecentActivity events={events} />
          <VoiceControlPanel lastCommand={events.find(e => e.event_type === 'voice_command')?.event_data?.description ?? ''} />
        </div>
      </div>
    </div>
  );
}
