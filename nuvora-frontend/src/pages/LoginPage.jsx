import { ParkingCircle } from 'lucide-react';

export default function LoginPage() {
  async function handleSubmit(e) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const username = form.get("email");      // ajusta nombres si cambian
    const password = form.get("password");

    const res = await fetch("/api/users/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      // manejo de error
      return;
    }
    const data = await res.json();
    localStorage.setItem("token", data.access_token);
    // redirigir a /dashboard
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
            type="email"
            placeholder="Correo electrónico"
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            required
          />
          <input
            type="password"
            placeholder="Contraseña"
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            required
          />
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition font-medium"
          >
            Entrar
          </button>
        </form>
      </div>
    </div>
  );
}
