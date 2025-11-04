import { Camera } from 'lucide-react';

export default function Detection() {
  // Simulación: resultados recientes, hora y “stream” falso
  const ultimaDeteccion = "ABC123";
  const horaUltima = "20:55:14";
  // Puedes reemplazar esta imagen/stream por un <video> en tiempo real en el futuro
  const placeholderImg = "http://localhost:8001/cameras/entrada/stream";

  return (
    <div className="max-w-4xl mx-auto py-10">
      <div className="flex items-center mb-6">
        <div className="bg-emerald-100 rounded-full p-2 mr-3">
          <Camera className="w-6 h-6 text-emerald-600" />
        </div>
        <h2 className="text-xl font-bold text-gray-900">Detección en Vivo</h2>
      </div>
      <div className="bg-white rounded-xl shadow p-6 border border-gray-100 flex flex-col md:flex-row gap-6">
        {/* Vista en vivo o imagen */}
        <div className="flex-1 flex flex-col items-center">
          <img
            src={placeholderImg}
            alt="Detección en vivo"
            className="rounded-lg object-cover w-full max-w-md mb-4"
          />
          <span className="text-xs text-gray-500">* Aquí puedes mostrar un <code>&lt;video&gt;</code> en tiempo real conectado a tu sistema</span>
        </div>
        {/* Detecciones recientes */}
        <div className="flex-1">
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-2 text-gray-900">Última placa detectada</h3>
            <div className="px-4 py-2 rounded-lg bg-slate-100 flex flex-col items-start">
              <span className="font-mono text-2xl tracking-widest text-blue-700">{ultimaDeteccion}</span>
              <span className="text-sm text-gray-500">Detectada a las {horaUltima}</span>
            </div>
          </div>
          <div>
            <h4 className="text-md font-semibold mb-1 text-gray-800">Placas recientes</h4>
            <ul className="text-sm text-gray-700 list-disc list-inside space-y-1">
              <li>XYZ987 - 20:54:32</li>
              <li>KLM456 - 20:49:03</li>
              <li>PRS789 - 20:45:24</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
