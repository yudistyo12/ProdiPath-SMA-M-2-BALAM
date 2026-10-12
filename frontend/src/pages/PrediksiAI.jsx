import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertCircle,
  ArrowLeft,
  BookOpen,
  BrainCircuit,
  CheckCircle2,
  Info,
  Sparkles,
  UserRound,
} from 'lucide-react';
import api from '../utils/api';

const initialValues = {
  nisn: '',
  nama: '',
  persetujuan_data: false,
  jurusan_sma: 'IPA',
  nilai_matematika: 80,
  nilai_sains: 80,
  nilai_sosial: 80,
  nilai_bahasa: 80,
  minat_teknologi: 3,
  minat_seni: 3,
  minat_komunikasi: 3,
  kemampuan_analitis: 3,
};

const indicators = [
  { name: 'nilai_matematika', label: 'Matematika', max: 100, score: true },
  { name: 'nilai_sains', label: 'Sains', max: 100, score: true },
  { name: 'nilai_sosial', label: 'Sosial', max: 100, score: true },
  { name: 'nilai_bahasa', label: 'Bahasa', max: 100, score: true },
  { name: 'minat_teknologi', label: 'Minat pada teknologi', max: 5 },
  { name: 'minat_seni', label: 'Minat pada seni', max: 5 },
  { name: 'minat_komunikasi', label: 'Minat pada komunikasi', max: 5 },
  { name: 'kemampuan_analitis', label: 'Kemampuan analitis', max: 5 },
];

export default function PrediksiAI() {
  const [formData, setFormData] = useState(initialValues);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setFormData((current) => ({
      ...current,
      [name]: type === 'checkbox'
        ? checked
        : ['jurusan_sma', 'nama', 'nisn'].includes(name)
          ? value
          : Number(value),
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await api.post('/predict/', formData);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Rekomendasi belum dapat diproses. Silakan coba lagi.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="recommendation-page min-h-screen">
      <header className="recommendation-header sticky top-0 z-20 border-b border-slate-200/80 bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-3 sm:px-8">
          <Link to="/" className="flex items-center gap-3 text-slate-900" aria-label="ProdiPath, kembali ke beranda">
            <span className="recommendation-brand-mark flex h-11 w-11 items-center justify-center overflow-hidden rounded-xl border bg-white p-0.5">
              <img src="/sma-m2-logo.png" alt="Logo SMA Muhammadiyah 2 Bandar Lampung" className="h-full w-full object-contain" />
            </span>
            <span>
              <span className="block text-lg font-extrabold leading-tight">ProdiPath</span>
              <span className="hidden text-[10px] font-semibold uppercase tracking-[0.13em] text-slate-500 sm:block">SMA Muhammadiyah 2 Bandar Lampung</span>
            </span>
          </Link>
          <Link to="/" className="recommendation-back inline-flex items-center gap-2 rounded-full px-3 py-2 text-sm font-semibold text-slate-600 transition">
            <ArrowLeft size={16} /> <span className="hidden sm:inline">Kembali ke</span> Beranda
          </Link>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-5 pb-12 pt-8 sm:px-8 sm:pb-16 sm:pt-11">
        <section className="recommendation-intro mb-8 max-w-3xl sm:mb-10">
          <div className="recommendation-eyebrow mb-4 inline-flex items-center gap-2 rounded-full px-3.5 py-2 text-xs font-bold uppercase tracking-[0.12em]">
            <Sparkles size={14} /> Panduan memilih jurusan
          </div>
          <h1 className="max-w-2xl text-3xl font-black leading-tight tracking-tight text-slate-950 sm:text-4xl">
            Kenali pilihan jurusan yang cocok untukmu
          </h1>
          <p className="mt-3 max-w-2xl text-base leading-7 text-slate-600 sm:text-lg">
            Isi data diri, nilai, dan minatmu. Hasilnya bisa menjadi bahan awal untuk mencari tahu jurusan kuliah.
          </p>
          <div className="recommendation-steps mt-6 grid max-w-2xl grid-cols-3 gap-2 sm:gap-3" aria-label="Langkah pengisian">
            {[
              ['1', 'Data diri'],
              ['2', 'Nilai rapor'],
              ['3', 'Minat'],
            ].map(([number, label]) => (
              <div key={number} className="flex items-center gap-2.5 text-sm font-semibold text-slate-600">
                <span className="recommendation-step-number flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold">{number}</span>
                {label}
              </div>
            ))}
          </div>
        </section>

        <div className="grid items-start gap-6 xl:grid-cols-[minmax(0,1.55fr)_minmax(320px,0.8fr)] xl:gap-8">
          <form onSubmit={handleSubmit} className="recommendation-form rounded-3xl border border-slate-200/80 bg-white p-5 shadow-[0_16px_55px_rgba(15,23,42,0.06)] sm:p-8 lg:p-9">
            <section className="recommendation-section recommendation-identity mb-8 rounded-2xl border p-5 sm:p-6">
              <div className="mb-5 flex items-start gap-3">
                <span className="recommendation-section-icon flex h-10 w-10 shrink-0 items-center justify-center rounded-xl">
                  <UserRound size={20} />
                </span>
                <div>
                  <h2 className="text-lg font-bold text-slate-900">Data diri</h2>
                  <p className="mt-1 text-sm leading-5 text-slate-600">Gunakan nama lengkap dan NISN yang benar.</p>
                </div>
              </div>
              <div className="grid gap-5 sm:grid-cols-2">
                <div>
                  <label htmlFor="nama" className="mb-2 block text-sm font-semibold text-slate-700">Nama lengkap</label>
                  <input
                    id="nama"
                    name="nama"
                    type="text"
                    autoComplete="name"
                    maxLength={100}
                    required
                    value={formData.nama}
                    onChange={handleChange}
                    placeholder="Masukkan nama lengkap"
                    className="recommendation-input w-full rounded-xl border bg-white px-4 py-3 text-slate-800 outline-none transition"
                  />
                </div>
                <div>
                  <label htmlFor="nisn" className="mb-2 block text-sm font-semibold text-slate-700">NISN</label>
                  <input
                    id="nisn"
                    name="nisn"
                    type="text"
                    inputMode="numeric"
                    autoComplete="off"
                    maxLength={10}
                    minLength={10}
                    pattern="[0-9]{10}"
                    title="NISN harus terdiri dari 10 angka."
                    required
                    value={formData.nisn}
                    onChange={handleChange}
                    placeholder="10 digit NISN"
                    className="recommendation-input w-full rounded-xl border bg-white px-4 py-3 text-slate-800 outline-none transition"
                  />
                  <p className="mt-1.5 text-xs leading-5 text-slate-500">NISN terdiri dari 10 angka. Jika ada angka nol di depan, tetap tuliskan.</p>
                </div>
              </div>
            </section>

            <div className="mb-9">
              <label htmlFor="jurusan_sma" className="mb-2 block text-sm font-bold text-slate-800">Peminatan di SMA</label>
              <select
                id="jurusan_sma"
                name="jurusan_sma"
                value={formData.jurusan_sma}
                onChange={handleChange}
                className="recommendation-input w-full rounded-xl border bg-white px-4 py-3 text-slate-800 outline-none transition"
              >
                <option value="IPA">IPA</option>
                <option value="IPS">IPS</option>
                <option value="Bahasa">Bahasa</option>
              </select>
            </div>

            <div className="recommendation-heading mb-5 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-start gap-3">
                <span className="recommendation-section-icon flex h-10 w-10 shrink-0 items-center justify-center rounded-xl">
                  <BookOpen size={20} />
                </span>
                <div>
                  <h2 className="text-lg font-bold text-slate-900">Nilai rapor</h2>
                  <p className="mt-1 text-sm text-slate-600">Pilih nilai terakhirmu untuk tiap mata pelajaran.</p>
                </div>
              </div>
              <span className="recommendation-chip rounded-full px-3 py-1.5 text-xs font-bold">Rentang 0–100</span>
            </div>
            <div className="grid gap-x-7 gap-y-5 sm:grid-cols-2">
              {indicators.filter((item) => item.score).map((item) => (
                <SliderField key={item.name} item={item} value={formData[item.name]} onChange={handleChange} />
              ))}
            </div>

            <div className="recommendation-heading mb-5 mt-9 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-7">
              <div>
                <h2 className="text-lg font-bold text-slate-900">Minat dan kemampuan</h2>
                <p className="mt-1 text-sm text-slate-600">Geser pilihan sesuai dengan dirimu.</p>
              </div>
              <span className="recommendation-chip rounded-full px-3 py-1.5 text-xs font-bold">Skala 1–5</span>
            </div>
            <div className="grid gap-x-7 gap-y-5 sm:grid-cols-2">
              {indicators.filter((item) => !item.score).map((item) => (
                <SliderField key={item.name} item={item} value={formData[item.name]} onChange={handleChange} />
              ))}
            </div>

            <label className="recommendation-consent mt-8 flex cursor-pointer items-start gap-3 rounded-2xl border p-4 text-sm leading-6 text-slate-700">
              <input
                type="checkbox"
                name="persetujuan_data"
                checked={formData.persetujuan_data}
                onChange={handleChange}
                required
                className="recommendation-checkbox mt-1 h-4 w-4 shrink-0"
              />
              <span>
                Saya setuju data diri dan jawaban ini disimpan agar dapat ditinjau oleh pengelola sekolah.
              </span>
            </label>

            {error && (
              <div role="alert" className="recommendation-error mt-6 flex items-start gap-3 rounded-xl border p-4 text-sm">
                <AlertCircle size={19} className="mt-0.5 shrink-0" />
                <p>{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="recommendation-submit mt-7 flex w-full items-center justify-center gap-2 rounded-xl px-5 py-4 font-bold text-white transition disabled:cursor-wait disabled:opacity-60"
            >
              {loading ? (
                <>
                  <span className="h-5 w-5 animate-spin rounded-full border-2 border-white/40 border-t-white" />
                  Sedang menyiapkan hasil...
                </>
              ) : (
                <>
                  <Sparkles size={19} /> Lihat rekomendasi
                </>
              )}
            </button>
          </form>

          <aside className="recommendation-aside space-y-4 xl:sticky xl:top-24">
            <section aria-live="polite" className={`recommendation-result rounded-3xl border p-6 text-center sm:p-8 ${result ? 'has-result' : ''}`}>
              {result ? (
                <>
                  <div className="recommendation-result-icon mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl text-white">
                    <CheckCircle2 size={30} />
                  </div>
                  <p className="recommendation-result-kicker text-xs font-bold uppercase tracking-[0.16em]">Hasil untuk</p>
                  <h2 className="mt-2 text-lg font-bold text-slate-800">{result.nama}</h2>
                  <p className="mt-5 text-sm font-semibold text-slate-600">Jurusan yang bisa kamu pertimbangkan</p>
                  <h3 className="recommendation-major mt-2 text-2xl font-black leading-tight sm:text-3xl">{result.prediksi}</h3>
                  <p className="mt-4 text-sm leading-6 text-slate-600">
                    Jawabanmu sudah tersimpan. Cari tahu lebih lanjut tentang mata kuliah dan kampus yang menawarkan jurusan ini.
                  </p>
                  <button
                    type="button"
                    onClick={() => { setResult(null); setError(''); }}
                    className="recommendation-retry mt-6 rounded-lg px-4 py-2 text-sm font-bold transition"
                  >
                    Isi ulang form
                  </button>
                </>
              ) : (
                <>
                  <div className="recommendation-empty-icon mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl">
                    <BrainCircuit size={29} />
                  </div>
                  <p className="recommendation-result-kicker text-xs font-bold uppercase tracking-[0.16em]">Hasil rekomendasi</p>
                  <h2 className="mt-3 text-xl font-bold text-slate-900">Hasilnya akan muncul di sini</h2>
                  <p className="mt-3 text-sm leading-6 text-slate-600">
                    Lengkapi form di samping, lalu tekan tombol “Lihat rekomendasi”.
                  </p>
                </>
              )}
            </section>

            <section className="recommendation-note rounded-2xl border p-5">
              <div className="flex items-start gap-3">
                <Info size={20} className="mt-0.5 shrink-0 text-amber-700" />
                <div>
                  <h3 className="font-bold text-amber-950">Tetap cari informasi lebih lanjut</h3>
                  <p className="mt-1 text-sm leading-6 text-amber-900/85">
                    Hasil ini hanya gambaran awal, bukan keputusan final. Diskusikan pilihanmu dengan guru BK dan cari informasi resmi dari kampus.
                  </p>
                </div>
              </div>
            </section>
            <p className="recommendation-privacy px-1 text-xs leading-5 text-slate-500">
              Data diri dan jawabanmu hanya dapat dilihat oleh pengelola sekolah yang berwenang.
            </p>
          </aside>
        </div>
      </div>
    </main>
  );
}

function SliderField({ item, value, onChange }) {
  return (
    <div>
      <label htmlFor={item.name} className="mb-2 flex items-center justify-between gap-3 text-sm font-semibold text-slate-700">
        <span>{item.label}</span>
        <span className="min-w-10 rounded-md bg-blue-50 px-2 py-1 text-center font-bold text-blue-700">{value}</span>
      </label>
      <input
        id={item.name}
        name={item.name}
        type="range"
        min={item.score ? 0 : 1}
        max={item.max}
        step="1"
        value={value}
        onChange={onChange}
        className="recommendation-range h-2 w-full cursor-pointer"
      />
      <div className="mt-2 flex justify-between text-[11px] font-medium text-slate-500">
        <span>{item.score ? '0' : '1 · Rendah'}</span>
        <span>{item.score ? '100' : '5 · Tinggi'}</span>
      </div>
    </div>
  );
}
