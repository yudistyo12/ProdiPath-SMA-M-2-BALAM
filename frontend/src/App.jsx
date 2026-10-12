import { BrowserRouter as Router, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import DashboardLayout from './components/DashboardLayout';
import Dashboard from './pages/Dashboard';
import ImportData from './pages/ImportData';
import Login from './pages/Login';
import MahasiswaList from './pages/MahasiswaList';
import PrediksiAI from './pages/PrediksiAI';

function ProtectedAdminRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="flex min-h-screen items-center justify-center text-slate-500">Memeriksa sesi...</div>;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (user.role !== 'admin') {
    return <Navigate to="/prediksi" replace />;
  }

  return <DashboardLayout>{children}</DashboardLayout>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/login" element={<Login />} />
      <Route path="/prediksi" element={<PrediksiAI />} />
      <Route path="/dashboard" element={<ProtectedAdminRoute><Dashboard /></ProtectedAdminRoute>} />
      <Route path="/mahasiswa" element={<ProtectedAdminRoute><MahasiswaList /></ProtectedAdminRoute>} />
      <Route path="/import" element={<ProtectedAdminRoute><ImportData /></ProtectedAdminRoute>} />
      <Route path="/profil" element={<Navigate to="/prediksi" replace />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
}

export default App;
