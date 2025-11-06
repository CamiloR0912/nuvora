import { useState, useEffect } from 'react';
import { StatCard } from '../components/StatCard';
import { ParkingSpaceGrid } from '../components/ParkingSpaceGrid';
import { VehicleList } from '../components/VehicleList';
import { RecentActivity } from '../components/RecentActivity';
import Detection from '../components/Detection';
import { Car, ParkingCircle, Clock, Mic } from 'lucide-react';
import { VoiceControlPanel } from '../components/VoiceControlPanel';
import axios from 'axios';

// Simulación de cupos (sigue igual, puedes cambiar por tu backend real luego)
const mockParkingSpaces = [
  { id: 1, floor: 1, zone: 'A', space_number: 'A1', is_occupied: false },
  { id: 2, floor: 1, zone: 'A', space_number: 'A2', is_occupied: true },
  { id: 3, floor: 1, zone: 'B', space_number: 'B1', is_occupied: false },
  { id: 4, floor: 2, zone: 'C', space_number: 'C1', is_occupied: true },
  { id: 5, floor: 2, zone: 'C', space_number: 'C2', is_occupied: false },
];

// Usamos el componente `VoiceControlPanel` real importado desde /components

export default function HomePage() {
  const [parkingSpaces, setParkingSpaces] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Cargar cupos simulados y datos reales de vehículos/eventos
    Promise.all([
      Promise.resolve(mockParkingSpaces),
      axios.get('/api/vehiculos/activos'),
      axios.get('/api/vehiculos/historial')
    ])
      .then(([mockSpaces, activosRes, historialRes]) => {
        setParkingSpaces(mockSpaces);

        // Mapea vehículos activos según API real
        setVehicles(
          activosRes.data.map(v => ({
            id: v.id,
            license_plate: v.placa,
            entry_time: new Date(v.fecha_entrada),
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
          created_at: v.fecha_entrada
        }));

        // Salidas
        const salidas = historialRes.data.map(v => ({
          id: `salida-${v.id}`,
          event_type: 'exit',
          event_data: {
            description: `Vehículo ${v.placa} salió del parqueadero`
          },
          created_at: v.fecha_salida
        }));

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

  const stats = {
    totalSpaces: parkingSpaces.length,
    occupiedSpaces: parkingSpaces.filter(s => s.is_occupied).length,
    availableSpaces: parkingSpaces.filter(s => !s.is_occupied).length,
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
      {/* Tarjetas de estadísticas principales */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard title="Total de Cupos" value={stats.totalSpaces} icon={ParkingCircle} subtitle="Capacidad total" />
        <StatCard title="Cupos Ocupados" value={stats.occupiedSpaces} icon={Car} subtitle={`${Math.round((stats.occupiedSpaces / stats.totalSpaces) * 100)}% ocupación`} />
        <StatCard title="Cupos Disponibles" value={stats.availableSpaces} icon={ParkingCircle} subtitle="Listos para usar" />
        <StatCard title="Vehículos Activos" value={stats.activeVehicles} icon={Clock} subtitle="En el parqueadero" />
      </div>

      {/* Aquí va el Detection, ocupa todo el ancho izquierdo del grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2">
          <Detection />
        </div>
        <div className="flex flex-col space-y-6">
          <RecentActivity events={events} />
          <VoiceControlPanel lastCommand={events.find(e => e.event_type === 'voice_command')?.event_data?.description ?? ''} />
        </div>
      </div>
      <VehicleList vehicles={vehicles} />
    </div>
  );
}
