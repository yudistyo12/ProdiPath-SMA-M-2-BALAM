import { useCallback, useEffect, useState } from 'react';
import { AlertCircle, Search, Trash2, Users } from 'lucide-react';
import api from '../utils/api';

export default function MahasiswaList() {
  const [students, setStudents] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchStudents = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get('/students/', { params: { search: search.trim() || undefined } });
      setStudents(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Gagal memuat data siswa. Periksa koneksi backend dan database.');
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    fetchStudents();
  }, [fetchStudents]);

  const handleDelete = async (nisn) => {
    if (!window.confirm('Hapus data siswa ini dari dataset?')) return;
    setError('');
    try {
      await api.delete(`/students/${encodeURIComponent(nisn)}`);
      await fetchStudents();
    } catch (err) {
      setError(err.response?.data?.detail || 'Data siswa gagal dihapus.');
    }
  };

  return (
    <div className="space-y-6">
      <section className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm font-semibold text-blue-700">Data pembelajaran model</p>
          <h2 className="mt-1 flex items-center gap-3 text-2xl font-black text-slate-900">
            <Users className="text-blue-600" /> Data Siswa
          </h2>
          <p className="mt-2 text-sm text-slate-500">Tinjau pengisian siswa dari web dan data latih yang diimpor.</p>
        </div>
        <div className="relative w-full sm:max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Cari NISN, nama, atau jurusan..."
            className="w-full rounded-xl border border-slate-200 bg-white py-3 pl-10 pr-4 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
          />
        </div>
      </section>

      {error && (
        <div role="alert" className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <AlertCircle size={18} className="mt-0.5 shrink-0" /> {error}
        </div>
      )}

      <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1200px] border-collapse text-left">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-xs font-bold uppercase tracking-wide text-slate-500">
                <th className="p-4">Siswa</th>
                <th className="p-4">Jurusan SMA</th>
                <th className="p-4">Nilai Matematika</th>
                <th className="p-4">Nilai Sains</th>
                <th className="p-4">Nilai Sosial</th>
                <th className="p-4">Nilai Bahasa</th>
                <th className="p-4">Hasil / label jurusan</th>
                <th className="p-4">Sumber</th>
                <th className="p-4">Persetujuan</th>
                <th className="p-4 text-right">Aksi</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr><td colSpan="10" className="p-10 text-center text-sm text-slate-500">Memuat data siswa...</td></tr>
              ) : students.length === 0 ? (
                <tr><td colSpan="10" className="p-10 text-center text-sm text-slate-500">Belum ada data yang cocok.</td></tr>
              ) : students.map((student) => (
                <tr key={student.nisn} className="transition hover:bg-slate-50/70">
                  <td className="p-4">
                    <p className="font-bold text-slate-800">{student.nama}</p>
                    <p className="mt-1 text-xs text-slate-500">NISN {student.nisn}</p>
                  </td>
                  <td className="p-4 text-sm text-slate-600">{student.jurusan_sma}</td>
                  <td className="p-4 text-sm font-semibold text-slate-700">{student.nilai_matematika}</td>
                  <td className="p-4 text-sm font-semibold text-slate-700">{student.nilai_sains}</td>
                  <td className="p-4 text-sm font-semibold text-slate-700">{student.nilai_sosial}</td>
                  <td className="p-4 text-sm font-semibold text-slate-700">{student.nilai_bahasa}</td>
                  <td className="p-4">
                    <span className="inline-flex rounded-full bg-blue-50 px-3 py-1.5 text-xs font-bold text-blue-800">{student.rekomendasi_jurusan}</span>
                  </td>
                  <td className="p-4">
                    <span className={`inline-flex rounded-full px-3 py-1.5 text-xs font-bold ${
                      student.sumber_data === 'kuesioner_web'
                        ? 'bg-teal-50 text-teal-800'
                        : 'bg-slate-100 text-slate-700'
                    }`}>
                      {student.sumber_data === 'kuesioner_web' ? 'Kuesioner web' : 'Data latih CSV'}
                    </span>
                  </td>
                  <td className="p-4 text-xs font-semibold text-slate-600">
                    {student.persetujuan_data ? 'Tercatat' : 'Tidak dicatat'}
                  </td>
                  <td className="p-4 text-right">
                    <button
                      type="button"
                      onClick={() => handleDelete(student.nisn)}
                      aria-label={`Hapus data ${student.nama}`}
                      title="Hapus data siswa"
                      className="rounded-lg p-2 text-slate-400 transition hover:bg-red-50 hover:text-red-600"
                    >
                      <Trash2 size={17} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="border-t border-slate-100 bg-slate-50/70 px-4 py-3 text-xs text-slate-500">
          Rekomendasi dari pengisian web merupakan hasil model, bukan label kebenaran; data tersebut tidak dihitung sebagai data latih pada ringkasan.
        </div>
      </section>
    </div>
  );
}
