import { useState, useEffect, useCallback } from 'react';
import { StatCard } from '../components/StatCard';
import { ParkingSpaceGrid } from '../components/ParkingSpaceGrid';
import { VehicleList } from '../components/VehicleList';
import { RecentActivity } from '../components/RecentActivity';
import Detection from '../components/Detection';
import { Car, ParkingCircle, Clock, Mic } from 'lucide-react';
import { VoiceControlPanel } from '../components/VoiceControlPanel';
import { VehicleManagementPanel } from '../components/VehicleManagementPanel';
import { useSSE } from '../api/useSSE';
import { http } from '../api/http';
import { useLocation } from 'react-router-dom';

const TOTAL_CUPOS = 30; // Cupos totales del parqueadero

export default function HomePage() {
  const location = useLocation();
  const [vehicles, setVehicles] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Estados para detecciones en tiempo real
  const [lastDetection, setLastDetection] = useState(null);
  const [recentDetections, setRecentDetections] = useState([]);

  // Estado para la placa que viene desde VehiculosPage
  const [placaSalidaInicial, setPlacaSalidaInicial] = useState(null);

  // Obtener token del localStorage
  const token = localStorage.getItem('token');

  // Detectar si vienen con una placa para registrar salida
  useEffect(() => {
    if (location.state?.placaSalida) {
      setPlacaSalidaInicial(location.state.placaSalida);
      // Limpiar el state para que no se quede persistente
      window.history.replaceState({}, document.title);
    }
  }, [location]);

  // Callback para manejar respuestas de comandos de voz
  const handleVoiceCommand = useCallback((voiceData) => {
    console.log('🎤 Comando de voz recibido:', voiceData);
    // Los comandos de voz ya no se agregan a la actividad reciente
  }, []);

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
      
      // Agregar evento a la actividad reciente
      const detectionEvent = {
        id: `detection-${Date.now()}`,
        event_type: 'entry',
        event_data: {
          description: `Vehículo ${data.placa} detectado entrando`
        },
        created_at: new Date().toISOString()
      };
      
      setEvents(prev => {
        const allEvents = [detectionEvent, ...prev];
        return allEvents
          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
          .slice(0, 3);
      });
      
      console.log('🚗 Vehículo detectado:', detection);
    }
  }, []);

  // Conectar a eventos SSE
  const { isConnected, error } = useSSE(
    'http://localhost:8000/api/events/stream',
    handleSSEMessage,
    token
  );

  // Función para agregar evento de salida manualmente
  const addExitEvent = useCallback((placa, ticketData) => {
    const exitEvent = {
      id: `salida-${Date.now()}`,
      event_type: 'exit',
      event_data: {
        description: `Vehículo ${placa} salió del parqueadero`
      },
      created_at: ticketData.hora_salida || new Date().toISOString()
    };
    
    setEvents(prev => {
      const allEvents = [exitEvent, ...prev];
      return allEvents
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 3);
    });
  }, []);

  // Función para recargar datos cuando se actualice un vehículo
  const loadVehicleData = () => {
    // Solo cargar tickets abiertos
    http.get('/tickets/abiertos')
      .then((response) => {
        const ticketsAbiertos = response.data;
        
        // Mapear tickets abiertos a formato de vehículos
        setVehicles(
          ticketsAbiertos.map(ticket => ({
            id: ticket.id,
            license_plate: ticket.placa,
            entry_time: new Date(ticket.hora_entrada),
            parking_spaces: { space_number: 'N/A' }
          }))
        );

        // Crear eventos de entradas (últimos 3 tickets abiertos)
        const entradas = ticketsAbiertos
          .sort((a, b) => new Date(b.hora_entrada) - new Date(a.hora_entrada))
          .slice(0, 3)
          .map(ticket => ({
            id: `entrada-${ticket.id}`,
            event_type: 'entry',
            event_data: {
              description: `Vehículo ${ticket.placa} ingresó al parqueadero`
            },
            created_at: ticket.hora_entrada
          }));

        // Mantener eventos de detección y salida que ya están en el estado
        setEvents(prevEvents => {
          const deteccionesYSalidas = prevEvents.filter(e => 
            e.event_type === 'exit' || e.id.startsWith('detection-')
          );
          const todosEventos = [...entradas, ...deteccionesYSalidas];
          
          return todosEventos
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
            .slice(0, 3);
        });
      })
      .catch((error) => {
        console.error('Error al cargar tickets:', error);
        setVehicles([]);
      });
  };

  useEffect(() => {
    // Cargar datos reales de vehículos/eventos
    loadVehicleData();
    setLoading(false);
  }, []); // Removida la dependencia loadVehicleData para evitar re-renders infinitos

  const stats = {
    totalSpaces: TOTAL_CUPOS,
    occupiedSpaces: vehicles.length, // Vehículos activos = cupos ocupados
    availableSpaces: TOTAL_CUPOS - vehicles.length, // Cupos disponibles
    activeVehicles: vehicles.length,
  };

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
      
      {/* Tarjeta de cupos - ocupa todo el ancho */}
      <div className="mb-6">
        <StatCard 
          title="Cupos" 
          value={`${stats.occupiedSpaces}/${stats.totalSpaces}`} 
          icon={ParkingCircle} 
          subtitle={`${Math.round((stats.occupiedSpaces / stats.totalSpaces) * 100)}% ocupación`} 
        />
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
          <VoiceControlPanel onCommandResponse={handleVoiceCommand} />
        </div>
      </div>

      {/* Panel de gestión de vehículos */}
      <div className="mb-8">
        <VehicleManagementPanel 
          onVehicleUpdate={loadVehicleData}
          onExitRegistered={addExitEvent}
          placaSalidaInicial={placaSalidaInicial}
          onPlacaSalidaUsada={() => setPlacaSalidaInicial(null)}
        />
      </div>
    </div>
  );
}
