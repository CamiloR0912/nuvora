import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Suspense, lazy } from 'react';

const HomePage = lazy(() => import('./pages/HomePage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={
        <div className="min-h-screen flex items-center justify-center bg-slate-50">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <span className="ml-4 text-gray-600 font-medium">Cargando página...</span>
        </div>
      }>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<HomePage />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;
