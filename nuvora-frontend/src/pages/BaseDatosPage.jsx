import React, { useEffect, useState } from "react";
import { getVehiculosHistorial, buscarPorPlaca } from "../api/vehiculosApi";
import { Search } from "lucide-react";

export default function BaseDatosPage() {
  const [historial, setHistorial] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busqueda, setBusqueda] = useState("");
  const [result, setResult] = useState(null);
  const [showError, setShowError] = useState(false);

  useEffect(() => {
    getVehiculosHistorial()
      .then(res => {
        Array.isArray(res.data) ? setHistorial(res.data) : setHistorial([]);
      })
      .catch(() => setHistorial([]))
      .finally(() => setLoading(false));
  }, []);

  const handleBuscar = async (e) => {
    e.preventDefault();
    setResult(null);
    setShowError(false);
    const placa = busqueda.trim().toUpperCase();
    if (!placa) {
      setShowError(true);
      return;
    }
    try {
      const res = await buscarPorPlaca(placa);
      setResult(res.data && res.data.vehiculo ? res.data : null);
      setShowError(!res.data || !res.data.vehiculo);
    } catch (err) {
      setShowError(true);
      setResult(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Registros en la base de datos</h2>
      <form className="flex gap-3 mb-8" onSubmit={handleBuscar}>
        <input
          type="text"
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value.toUpperCase())}
          placeholder="Buscar por placa (ejemplo: ABC123)"
          className="p-2 border rounded w-60 font-mono tracking-widest"
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded flex gap-2 items-center"
        >
          <Search className="w-4 h-4" />
          Buscar
        </button>
      </form>

      {showError && (
        <div className="mb-4">
          <div className="bg-red-600 text-white text-center font-bold py-3 px-4 rounded shadow">
            no existe la placa
          </div>
        </div>
      )}

      {result && result.vehiculo && (
        <div className="bg-white border rounded-xl shadow p-6 text-gray-800 mb-6">
          <h3 className="text-lg font-bold mb-2">
            Resultado encontrado ({result.estado === "activo" ? "Activo" : "Historial"})
          </h3>
          <table className="min-w-full mb-1">
            <tbody>
              <tr>
                <td className="font-semibold pr-2">Placa:</td>
                <td className="font-mono">{result.vehiculo.placa}</td>
              </tr>
              <tr>
                <td className="font-semibold pr-2">
                  {result.estado === "activo" ? "Ingreso:" : "Entrada:"}
                </td>
                <td>{new Date(result.vehiculo.fecha_entrada).toLocaleString()}</td>
              </tr>
              {result.estado === "historial" && (
                <>
                  <tr>
                    <td className="font-semibold pr-2">Salida:</td>
                    <td>{new Date(result.vehiculo.fecha_salida).toLocaleString()}</td>
                  </tr>
                  <tr>
                    <td className="font-semibold pr-2">Total facturado:</td>
                    <td>${result.vehiculo.total_facturado.toLocaleString()}</td>
                  </tr>
                </>
              )}
            </tbody>
          </table>
        </div>
      )}

      <div className="overflow-x-auto shadow-sm rounded border border-gray-200 bg-white">
        {loading ? (
          <div className="text-center py-8 text-gray-500">Cargando...</div>
        ) : historial.length === 0 ? (
          <div className="p-8 text-center text-gray-500 text-lg">No hay registros en la base de datos.</div>
        ) : (
          <table className="min-w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="py-3 px-4 text-left text-gray-600 font-semibold">Placa</th>
                <th className="py-3 px-4 text-left text-gray-600 font-semibold">Entrada</th>
                <th className="py-3 px-4 text-left text-gray-600 font-semibold">Salida</th>
                <th className="py-3 px-4 text-left text-gray-600 font-semibold">Total facturado</th>
              </tr>
            </thead>
            <tbody>
              {historial.map(v => (
                <tr key={v.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono text-lg">{v.placa}</td>
                  <td className="px-4 py-3">{new Date(v.fecha_entrada).toLocaleString()}</td>
                  <td className="px-4 py-3">{new Date(v.fecha_salida).toLocaleString()}</td>
                  <td className="px-4 py-3 text-green-700 font-bold">${v.total_facturado.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}