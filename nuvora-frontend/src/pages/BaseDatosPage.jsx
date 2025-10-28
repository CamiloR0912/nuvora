import React, { useState } from 'react';

// Datos simulados sin el campo de dueño
const allVehiculos = [
  { id: 1, placa: 'ABC123', ingreso: '2025-10-27 10:05', espacio: 'A2' },
  { id: 2, placa: 'XYZ987', ingreso: '2025-10-27 13:27', espacio: 'C1' },
  { id: 3, placa: 'PRS789', ingreso: '2025-10-27 15:00', espacio: 'B3' },
  // ...agrega más aquí para probar paginación
];

const ROWS_PER_PAGE = 2;

export default function BaseDatosPage() {
  const [page, setPage] = useState(1);

  const pageCount = Math.ceil(allVehiculos.length / ROWS_PER_PAGE);
  const datos = allVehiculos.slice((page - 1) * ROWS_PER_PAGE, page * ROWS_PER_PAGE);

  function handleNext() {
    setPage((p) => Math.min(p + 1, pageCount));
  }
  function handlePrev() {
    setPage((p) => Math.max(p - 1, 1));
  }

  return (
    <div className="max-w-4xl mx-auto py-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Vehículos registrados en la base de datos</h2>
      
      {datos.length === 0 ? (
        <div className="bg-white rounded-xl shadow p-8 text-center text-gray-500 text-lg">
          No hay registros en la base de datos.
        </div>
      ) : (
        <div className="overflow-x-auto shadow-sm rounded border border-gray-200 bg-white">
          <table className="min-w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="py-3 px-4 text-left text-gray-600 font-semibold">Placa</th>
                <th className="py-3 px-4 text-left text-gray-600 font-semibold">Ingreso</th>
                <th className="py-3 px-4 text-left text-gray-600 font-semibold">Espacio</th>
              </tr>
            </thead>
            <tbody>
              {datos.map((v) => (
                <tr key={v.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono text-lg">{v.placa}</td>
                  <td className="px-4 py-3">{v.ingreso}</td>
                  <td className="px-4 py-3">{v.espacio}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Controles de paginación */}
      <div className="flex items-center justify-between mt-4">
        <span className="text-sm text-gray-600">
          Página {page} de {pageCount}
        </span>
        <div>
          <button
            onClick={handlePrev}
            disabled={page === 1}
            className="px-4 py-1 mr-2 bg-slate-100 text-slate-600 rounded disabled:bg-slate-50 disabled:text-slate-400"
          >
            Anterior
          </button>
          <button
            onClick={handleNext}
            disabled={page === pageCount}
            className="px-4 py-1 bg-slate-100 text-slate-600 rounded disabled:bg-slate-50 disabled:text-slate-400"
          >
            Siguiente
          </button>
        </div>
      </div>
    </div>
  );
}
