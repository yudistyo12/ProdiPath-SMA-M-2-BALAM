import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { User, BookOpen, BrainCircuit, CheckCircle, Send, RefreshCcw, Info } from 'lucide-react';

export default function ProfilSaya() {
  const { user } = useAuth();
  const [profil, setProfil] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [prediksiResult, setPrediksiResult] = useState(null);

  const [formData, setFormData] = useState({
    konsistensi_belajar: 3,
    manajemen_waktu: 3,
    penyelesaian_tugas: 3,
    pemahaman_materi: 3,
    konsentrasi_belajar: 3,
    persiapan_ujian: 3,
    keaktifan_pembelajaran: 3,
    motivasi_belajar: 3,
    pemanfaatan_waktu_belajar: 3
  });

  const indicators = [
    { name: 'konsistensi_belajar', label: 'Konsistensi Belajar', desc: 'Seberapa rutin Anda belajar setiap hari' },
    { name: 'manajemen_waktu', label: 'Manajemen Waktu', desc: 'Kemampuan mengatur jadwal belajar' },
    { name: 'penyelesaian_tugas', label: 'Penyelesaian Tugas', desc: 'Ketepatan waktu menyelesaikan tugas' },
    { name: 'pemahaman_materi', label: 'Pemahaman Materi', desc: 'Tingkat pemahaman terhadap materi kuliah' },
    { name: 'konsentrasi_belajar', label: 'Konsentrasi Belajar', desc: 'Fokus saat belajar di kelas/rumah' },
    { name: 'persiapan_ujian', label: 'Persiapan Ujian', desc: 'Persiapan menjelang ujian/kuis' },
    { name: 'keaktifan_pembelajaran', label: 'Keaktifan Pembelajaran', desc: 'Partisipasi aktif di kelas' },
    { name: 'motivasi_belajar', label: 'Motivasi Belajar', desc: 'Dorongan dan semangat belajar' },
    { name: 'pemanfaatan_waktu_belajar', label: 'Pemanfaatan Waktu Belajar', desc: 'Efektivitas penggunaan waktu luang' }
  ];

  const scaleLabels = ['Sangat Rendah', 'Rendah', 'Cukup', 'Baik', 'Sangat Baik'];

  useEffect(() => {
    fetchProfil();
  }, []);

  const fetchProfil = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get('http://localhost:8000/api/mahasiswa/profil', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProfil(res.data);

      // Jika sudah pernah isi kuesioner, isi form dengan data yang ada
      if (res.data.questionnaire) {
        const q = res.data.questionnaire;
        setFormData({
          konsistensi_belajar: q.konsistensi_belajar,
          manajemen_waktu: q.manajemen_waktu,
          penyelesaian_tugas: q.penyelesaian_tugas,
          pemahaman_materi: q.pemahaman_materi,
          konsentrasi_belajar: q.konsentrasi_belajar,
          persiapan_ujian: q.persiapan_ujian,
          keaktifan_pembelajaran: q.keaktifan_pembelajaran,
          motivasi_belajar: q.motivasi_belajar,
          pemanfaatan_waktu_belajar: q.pemanfaatan_waktu_belajar
        });
      }

      if (res.data.prediction) {
        setPrediksiResult(res.data.prediction.predicted_performance);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: parseInt(e.target.value) });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setSuccessMsg('');
    try {
      const token = localStorage.getItem('token');
      const res = await axios.post('http://localhost:8000/api/mahasiswa/kuesioner', formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSuccessMsg(res.data.message);
      setPrediksiResult(res.data.prediksi_ai);
      fetchProfil(); // Refresh profil
    } catch (err) {
      alert(err.response?.data?.detail || 'Gagal menyimpan kuesioner.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64 text-slate-500">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mr-3"></div>
      Memuat profil...
    </div>
  );

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header Profil */}
      <div className="glass-panel p-6 flex flex-col sm:flex-row sm:items-center gap-6">
        <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center text-primary-600 shrink-0">
          <User size={32} />
        </div>
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-slate-800">Profil Saya</h2>
          <div className="flex flex-wrap gap-x-6 gap-y-1 mt-2 text-sm text-slate-600">
            <span><strong>NPM:</strong> {profil?.npm}</span>
            <span><strong>Program Studi:</strong> {profil?.program_studi}</span>
            <span><strong>Semester:</strong> {profil?.semester}</span>
          </div>
        </div>
        {prediksiResult && (
          <div className={`px-5 py-3 rounded-xl text-center shrink-0 ${
            prediksiResult === 'Tinggi' ? 'bg-emerald-50 border border-emerald-200' : 
            prediksiResult === 'Sedang' ? 'bg-amber-50 border border-amber-200' : 
            'bg-red-50 border border-red-200'
          }`}>
            <p className="text-xs font-semibold text-slate-500 mb-1">Prediksi AI</p>
            <p className={`text-2xl font-black ${
              prediksiResult === 'Tinggi' ? 'text-emerald-700' : 
              prediksiResult === 'Sedang' ? 'text-amber-700' : 
              'text-red-700'
            }`}>{prediksiResult}</p>
          </div>
        )}
      </div>

      {/* Success Message */}
      {successMsg && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-xl p-4 flex items-center animate-fade-in">
          <CheckCircle className="mr-3 shrink-0" size={20} />
          <p className="text-sm font-medium">{successMsg}</p>
        </div>
      )}

      {/* Form Kuesioner */}
      <div className="glass-panel p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <BookOpen className="mr-3 text-primary-600" size={22} />
            <div>
              <h3 className="text-lg font-bold text-slate-800">Kuesioner Kebiasaan Belajar</h3>
              <p className="text-sm text-slate-500">Isi sesuai kebiasaan belajar Anda (skala 1-5)</p>
            </div>
          </div>
          <span className="text-xs font-semibold bg-blue-100 text-blue-700 px-3 py-1 rounded-full">Skala Likert 1 - 5</span>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid grid-cols-1 gap-5">
            {indicators.map((ind) => (
              <div key={ind.name} className="bg-slate-50/50 rounded-xl p-4 border border-slate-100 hover:border-primary-200 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <label className="text-sm font-semibold text-slate-700">{ind.label}</label>
                    <p className="text-xs text-slate-400 mt-0.5">{ind.desc}</p>
                  </div>
                  <span className={`text-lg font-bold min-w-[2rem] text-center rounded-lg px-2 py-0.5 ${
                    formData[ind.name] >= 4 ? 'text-emerald-700 bg-emerald-50' : 
                    formData[ind.name] >= 3 ? 'text-amber-700 bg-amber-50' : 
                    'text-red-700 bg-red-50'
                  }`}>{formData[ind.name]}</span>
                </div>
                <input 
                  type="range" 
                  min="1" 
                  max="5" 
                  step="1"
                  name={ind.name} 
                  value={formData[ind.name]} 
                  onChange={handleChange} 
                  className="w-full accent-primary-600 h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer" 
                />
                <div className="flex justify-between text-[10px] text-slate-400 mt-1.5 px-0.5">
                  {scaleLabels.map((label, i) => (
                    <span key={i} className={formData[ind.name] === i + 1 ? 'text-primary-600 font-semibold' : ''}>{label}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="pt-6 border-t border-slate-100 flex flex-col sm:flex-row gap-3">
            <button 
              type="submit" 
              disabled={submitting}
              className="flex-1 bg-primary-600 hover:bg-primary-700 text-white font-medium py-3.5 rounded-xl transition-all shadow-md hover:shadow-lg disabled:bg-primary-300 flex items-center justify-center"
            >
              {submitting ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                  Memproses...
                </>
              ) : (
                <>
                  <Send className="mr-2" size={18} />
                  {profil?.questionnaire ? 'Perbarui Kuesioner & Jalankan Prediksi AI' : 'Kirim Kuesioner & Jalankan Prediksi AI'}
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Info Box */}
      <div className="glass-panel p-5 bg-indigo-50/50 border-indigo-100 flex gap-3">
        <Info className="text-indigo-500 shrink-0 mt-0.5" size={18} />
        <div className="text-sm text-slate-600 leading-relaxed">
          <p className="font-semibold text-slate-700 mb-1">Bagaimana prediksi ini bekerja?</p>
          <p>Setelah Anda mengisi kuesioner, sistem akan otomatis menjalankan model AI (Decision Tree) untuk memprediksi kategori performa belajar Anda berdasarkan pola kebiasaan belajar yang Anda isi. Hasil prediksi akan langsung tampil di profil Anda.</p>
        </div>
      </div>
    </div>
  );
}
