import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ParkingCircle } from "lucide-react";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [montoInicial, setMontoInicial] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    const payload = {
      username: username.trim(),
      password,
      monto_inicial: montoInicial ? parseFloat(montoInicial) : 0.0,
    };

    try {
      const res = await fetch("/api/users/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        let msg = "Error en autenticación";
        try {
          const body = await res.json();
          if (body && body.detail) msg = body.detail;
        } catch (_) {}
        setError(msg);
        setLoading(false);
        return;
      }

      const data = await res.json();
      if (!data || !data.access_token) {
        setError("Respuesta inválida del servidor");
        setLoading(false);
        return;
      }

      // Guardar token e información del usuario y turno
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("usuario", JSON.stringify(data.usuario));
      localStorage.setItem("turno", JSON.stringify(data.turno));

      navigate("/dashboard");
    } catch (err) {
      setError("Error de red o servidor: " + (err.message || ""));
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
          Iniciar Sesión
        </h2>

        <form className="space-y-5" onSubmit={handleSubmit}>
          <input
            name="username"
            type="text"
            placeholder="Usuario"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            required
          />

          <input
            name="password"
            type="password"
            placeholder="Contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            required
          />

          <input
            name="montoInicial"
            type="number"
            step="0.01"
            placeholder="Monto inicial (ej: 20000)"
            value={montoInicial}
            onChange={(e) => setMontoInicial(e.target.value)}
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            required
          />

          {error && (
            <div className="text-red-600 text-sm text-center">{error}</div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition font-medium disabled:opacity-60"
          >
            {loading ? "Ingresando..." : "Entrar"}
          </button>
        </form>
      </div>
    </div>
  );
}
