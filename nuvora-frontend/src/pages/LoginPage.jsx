import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ParkingCircle } from "lucide-react";
import { jwtDecode } from "jwt-decode";

function toErrorMessage(body, fallback = "Error en autenticación") {
  if (!body) return fallback;
  const detail = body.detail ?? body;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((d) => d?.msg || JSON.stringify(d)).join(", ");
  try { return JSON.stringify(detail); } catch { return fallback; }
}

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState("");
  const navigate = useNavigate();

  async function tryLoginJson(payload) {
    if (!payload.username || !payload.password) {
      throw new Error("Usuario y contraseña son obligatorios");
    }

    const res = await fetch("/api/users/login", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload),
    });

    if (res.status === 422) {
      const errorBody = await res.json().catch(() => ({}));
      throw new Error(toErrorMessage(errorBody, "Datos inválidos en el JSON"));
    }

    return res;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await tryLoginJson({ username: username.trim(), password });
      if (!res.ok) {
        const text = await res.text().catch(() => "");
        let msg = text;
        try {
          const body = text ? JSON.parse(text) : null;
          msg = toErrorMessage(body, "Error en autenticación");
        } catch {}

        setError(msg || "Error en autenticación");
        return;
      }

      const data = await res.json().catch(() => null);
      if (!data || (!data.access_token && !data.token)) {
        setError("Respuesta inválida del servidor");
        return;
      }

      const accessToken = data.access_token || data.token;
      localStorage.setItem("token", accessToken);

      // Decodificar el token para verificar turno_id
      let hasTurno = false;
      try {
        const decodedToken = jwtDecode(accessToken);
        console.log("Token decodificado:", decodedToken);
        hasTurno = decodedToken.turno_id != null;
        console.log("¿Tiene turno?", hasTurno, "turno_id:", decodedToken.turno_id);
      } catch (err) {
        console.error("Error al decodificar el token JWT:", err);
      }

      // Obtener datos del usuario (no bloqueante)
      fetch("/api/users/me", {
        headers: { Authorization: "Bearer " + accessToken, Accept: "application/json" },
      })
        .then(meRes => meRes.ok ? meRes.json() : null)
        .then(me => {
          if (me) localStorage.setItem("usuario", JSON.stringify(me));
          else localStorage.removeItem("usuario");
        })
        .catch(() => localStorage.removeItem("usuario"));

      // Solo intentar obtener turno si el token tiene turno_id (no bloqueante)
      if (hasTurno) {
        fetch("/api/turnos/actual", {
          headers: { Authorization: "Bearer " + accessToken, Accept: "application/json" },
        })
          .then(turnoRes => turnoRes.ok ? turnoRes.json() : null)
          .then(turno => {
            if (turno) localStorage.setItem("turno", JSON.stringify(turno));
            else localStorage.removeItem("turno");
          })
          .catch(() => localStorage.removeItem("turno"));
      } else {
        localStorage.removeItem("turno");
      }

      // Redirigir inmediatamente según tenga o no turno activo
      console.log("Navegando a:", hasTurno ? "/dashboard" : "/start-shift");
      console.log("Token guardado en localStorage:", localStorage.getItem("token"));
      
      const targetRoute = hasTurno ? "/dashboard" : "/start-shift";
      console.log("Ejecutando navigate a:", targetRoute);
      navigate(targetRoute, { replace: true });
      console.log("Navigate ejecutado");
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