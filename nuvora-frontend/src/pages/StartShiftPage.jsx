import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ParkingCircle } from "lucide-react";

function toErrorMessage(body, fallback = "No se pudo iniciar el turno") {
  if (!body) return fallback;
  const detail = body.detail ?? body;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const msgs = detail.map((d) => d?.msg || JSON.stringify(d));
    return msgs.join(", ");
  }
  try {
    return JSON.stringify(detail);
  } catch {
    return fallback;
  }
}

export default function StartShiftPage() {
  const [montoInicial, setMontoInicial] = useState("");
  const [observaciones, setObservaciones] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login", { replace: true });
      return;
    }

    const amount = parseFloat(montoInicial);
    if (!montoInicial || isNaN(amount) || amount <= 0) {
      setError("El monto inicial es obligatorio y debe ser mayor a 0");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("/api/turnos/iniciar", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ monto_inicial: amount, observaciones }),
      });

      if (!res.ok) {
        let msg = "No se pudo iniciar el turno";
        try {
          const body = await res.json();
          msg = toErrorMessage(body);
        } catch (_) {}
        setError(msg);
        return;
      }

      const data = await res.json(); // TurnoIniciadoResponse con access_token
      if (!data || !data.access_token) {
        setError("Respuesta inválida del servidor");
        return;
      }

      // Reemplazar token por el que incluye turno_id
      localStorage.setItem("token", data.access_token);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError("Error de red o servidor: " + (err?.message || ""));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-blue-100">
      <div className="bg-white p-8 rounded-xl shadow-md w-full max-w-md">
        <div className="flex justify-center mb-6">
          <div className="bg-blue-600 p-3 rounded-xl">
            <ParkingCircle className="w-10 h-10 text-white" />
          </div>
        </div>
        <h2 className="text-2xl font-bold text-center text-gray-900 mb-6">
          Iniciar turno
        </h2>

        <form className="space-y-5" onSubmit={handleSubmit}>
          <input
            name="montoInicial"
            type="number"
            min="0.01"
            step="0.01"
            placeholder="Monto inicial (ej: 20000)"
            value={montoInicial}
            onChange={(e) => setMontoInicial(e.target.value)}
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            required
          />

          <textarea
            name="observaciones"
            placeholder="Observaciones (opcional)"
            value={observaciones}
            onChange={(e) => setObservaciones(e.target.value)}
            rows={3}
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />

          {error && (
            <div className="text-red-600 text-sm text-center">{error}</div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition font-medium disabled:opacity-60"
          >
            {loading ? "Guardando..." : "Comenzar turno"}
          </button>
        </form>
      </div>
    </div>
  );
}
