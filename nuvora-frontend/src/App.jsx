import './index.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';

// Datos simulados para pruebas
const mockParkingSpaces = [
  { id: 1, floor: 1, zone: 'A', space_number: 'A1', is_occupied: false },
  { id: 2, floor: 1, zone: 'A', space_number: 'A2', is_occupied: true },
  { id: 3, floor: 1, zone: 'B', space_number: 'B1', is_occupied: false },
  { id: 4, floor: 2, zone: 'C', space_number: 'C1', is_occupied: true },
  { id: 5, floor: 2, zone: 'C', space_number: 'C2', is_occupied: false },
];

const mockVehicles = [
  {
    id: 1,
    license_plate: 'ABC123',
    entry_time: new Date(Date.now() - 1000 * 60 * 45), // hace 45 min
    parking_spaces: { space_number: 'A2' },
  },
  {
    id: 2,
    license_plate: 'XYZ987',
    entry_time: new Date(Date.now() - 1000 * 60 * 120), // hace 2h
    parking_spaces: { space_number: 'C1' },
  },
];

const mockEvents = [
  {
    id: 1,
    event_type: 'entry',
    event_data: { description: 'Vehículo ABC123 ingresó al parqueadero' },
    created_at: new Date(Date.now() - 1000 * 60 * 5), // hace 5 min
  },
  {
    id: 2,
    event_type: 'exit',
    event_data: { description: 'Vehículo KLM456 salió del parqueadero' },
    created_at: new Date(Date.now() - 1000 * 60 * 30),
  },
  {
    id: 3,
    event_type: 'voice_command',
    event_data: { description: 'Comando de voz ejecutado: “Mostrar ocupación nivel 2”' },
    created_at: new Date(Date.now() - 1000 * 60 * 60),
  },
];

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        {/* futuras rutas: <Route path="/otra" element={<OtherPage/>} /> */}
      </Routes>
    </BrowserRouter>
  );
}

export default App;
