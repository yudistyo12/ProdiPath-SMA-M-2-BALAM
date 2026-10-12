import { Link, useLocation } from 'react-router-dom';
import { ArrowUpRight, BrainCircuit, Database, LayoutDashboard, LogOut, Users } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const menu = [
  { path: '/dashboard', name: 'Ringkasan', icon: LayoutDashboard },
  { path: '/mahasiswa', name: 'Data Siswa', icon: Users },
  { path: '/import', name: 'Dataset', icon: Database },
];

export default function DashboardLayout({ children }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const currentPage = menu.find((item) => item.path === location.pathname)?.name || 'Panel Pengelola';

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="flex w-64 shrink-0 flex-col border-r border-slate-200 bg-white">
        <Link to="/dashboard" className="flex h-20 items-center gap-3 border-b border-slate-100 px-6">
          <span className="flex h-11 w-11 shrink-0 items-center justify-center overflow-hidden rounded-xl border border-slate-100 bg-white p-0.5">
            <img src="/sma-m2-logo.png" alt="Logo SMA Muhammadiyah 2 Bandar Lampung" className="h-full w-full object-contain" />
          </span>
          <div>
            <p className="text-lg font-extrabold tracking-tight text-slate-900">ProdiPath</p>
            <p className="text-[11px] font-medium text-slate-500">PANEL PENGELOLA</p>
          </div>
        </Link>

        <div className="flex-1 px-4 py-7">
          <p className="mb-3 px-3 text-[11px] font-bold uppercase tracking-[0.16em] text-slate-400">Menu utama</p>
          <nav className="space-y-1">
            {menu.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-3 rounded-xl px-3 py-3 text-sm transition ${
                    isActive
                      ? 'bg-emerald-50 font-bold text-emerald-800'
                      : 'font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  }`}
                >
                  <Icon size={19} />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          <Link
            to="/prediksi"
            className="dashboard-sidebar-cta mt-8 flex items-center justify-between rounded-2xl p-4 text-white transition"
          >
            <span>
              <span className="flex items-center gap-2 text-sm font-bold"><BrainCircuit size={17} /> Form rekomendasi</span>
              <span className="mt-1 block text-xs text-slate-400">Lihat tampilan siswa</span>
            </span>
            <ArrowUpRight size={17} />
          </Link>
        </div>

        <div className="border-t border-slate-100 p-4">
          <div className="mb-3 rounded-xl bg-slate-50 p-3">
            <p className="truncate text-sm font-bold text-slate-800">{user?.username}</p>
            <p className="mt-0.5 text-xs capitalize text-slate-500">{user?.role === 'admin' ? 'Administrator' : user?.role}</p>
          </div>
          <button
            onClick={logout}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold text-slate-600 transition hover:bg-red-50 hover:text-red-600"
          >
            <LogOut size={18} /> Keluar
          </button>
        </div>
      </aside>

      <main className="min-w-0 flex-1 overflow-y-auto">
        <header className="sticky top-0 z-10 flex h-20 items-center border-b border-slate-200 bg-white/90 px-6 backdrop-blur sm:px-9">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">ProdiPath</p>
            <h1 className="mt-0.5 text-lg font-bold text-slate-900">{currentPage}</h1>
          </div>
        </header>
        <div className="mx-auto max-w-7xl p-5 sm:p-8">{children}</div>
      </main>
    </div>
  );
}
