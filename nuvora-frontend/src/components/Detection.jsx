import { Camera } from 'lucide-react';

export default function Detection() {
  const ultimaDeteccion = "ABC123";
  const horaUltima = "20:55:14";
  const placeholderImg = "http://localhost:8001/cameras/entrada/stream";
  
  return (
    <div className="bg-white rounded-xl shadow p-8 border border-gray-100 w-full h-full flex flex-col">
      {/* Cabecera */}
      <div className="flex items-center mb-6">
        <div className="bg-emerald-100 rounded-full p-2 mr-3">
          <Camera className="w-6 h-6 text-emerald-600" />
        </div>
        <h2 className="text-xl font-bold text-gray-900">Detección en Vivo</h2>
      </div>
      {/* Contenido mayor video, menor info */}
      <div className="flex flex-col md:flex-row gap-8">
        {/* Video más grande */}
        <div className="flex-[2] min-w-[240px] flex items-center justify-center">
          <div className="flex items-center justify-center bg-slate-200 rounded-lg w-full aspect-video h-[330px] md:h-[360px]">
            <span className="text-2xl font-bold text-gray-400">Video en vivo</span>
          </div>
          {/* Para stream real: 
          <img src={placeholderImg} className="rounded-lg w-full h-[360px] object-cover" />
          */}
        </div>
        {/* Detalle, info más pequeña */}
        <div className="flex-[1] max-w-xs flex flex-col justify-center">
          <h3 className="text-base font-semibold mb-2 text-gray-900">Última placa detectada</h3>
          <div className="px-4 py-2 rounded-lg bg-slate-100 flex flex-col items-start mb-4">
            <span className="font-mono text-xl tracking-widest text-blue-700">{ultimaDeteccion}</span>
            <span className="text-xs text-gray-500">Detectada a las {horaUltima}</span>
          </div>
          <h4 className="text-sm font-semibold mb-1 text-gray-800">Placas recientes</h4>
          <ul className="text-xs text-gray-700 list-disc list-inside space-y-1">
            <li>XYZ987 - 20:54:32</li>
            <li>KLM456 - 20:49:03</li>
            <li>PRS789 - 20:45:24</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
