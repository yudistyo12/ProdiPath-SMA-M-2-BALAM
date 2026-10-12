import { useLayoutEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AlertCircle, ArrowRight, BookOpenCheck, Sparkles } from 'lucide-react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { useAuth } from '../context/AuthContext';

gsap.registerPlugin(ScrollTrigger);

export default function Login() {
  const pageRef = useRef(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  useLayoutEffect(() => {
    const motionQuery = gsap.matchMedia();

    motionQuery.add('(prefers-reduced-motion: no-preference)', () => {
      const context = gsap.context(() => {
        const createInfiniteLoop = (target, waypoints, duration) => {
          const loop = gsap.timeline({ repeat: -1 });
          waypoints.forEach((waypoint) => {
            loop.to(target, {
              ...waypoint,
              duration,
              ease: 'sine.inOut',
            });
          });
        };

        createInfiniteLoop(
          '.landing-background',
          [
            { scale: 1.025, xPercent: 0.6, yPercent: -0.35 },
            { scale: 1.035, xPercent: -0.5, yPercent: 0.4 },
            { scale: 1.015, xPercent: 0, yPercent: 0 },
          ],
          24
        );

        createInfiniteLoop(
          '.mesh-blob--blue',
          [
            { x: '7vw', y: '6vh', scale: 1.12 },
            { x: '3vw', y: '-4vh', scale: 0.96 },
            { x: '-2vw', y: '2vh', scale: 1.04 },
            { x: 0, y: 0, scale: 1 },
          ],
          14
        );

        createInfiniteLoop(
          '.mesh-blob--cyan',
          [
            { x: '-6vw', y: '5vh', scale: 1.1 },
            { x: '-2vw', y: '-5vh', scale: 0.96 },
            { x: '4vw', y: '2vh', scale: 1.04 },
            { x: 0, y: 0, scale: 1 },
          ],
          16
        );

        createInfiniteLoop(
          '.mesh-blob--violet',
          [
            { x: '5vw', y: '-6vh', scale: 1.12 },
            { x: '-4vw', y: '-2vh', scale: 0.96 },
            { x: '-2vw', y: '5vh', scale: 1.04 },
            { x: 0, y: 0, scale: 1 },
          ],
          18
        );

        createInfiniteLoop(
          '.mesh-blob--sky',
          [
            { x: '-4vw', y: '6vh', scale: 1.1 },
            { x: '-2vw', y: '-4vh', scale: 0.96 },
            { x: '4vw', y: '2vh', scale: 1.04 },
            { x: 0, y: 0, scale: 1 },
          ],
          15
        );

        gsap.utils.toArray('[data-auto-reveal]', pageRef.current).forEach((element, index) => {
          gsap.fromTo(
            element,
            { autoAlpha: 0, y: 34, filter: 'blur(8px)' },
            {
              autoAlpha: 1,
              y: 0,
              filter: 'blur(0px)',
              duration: 0.9,
              delay: (index % 5) * 0.08,
              ease: 'power3.out',
              clearProps: 'filter,transform',
              scrollTrigger: {
                trigger: element,
                start: 'top 88%',
                once: true,
              },
            }
          );
        });
      }, pageRef);

      return () => context.revert();
    });

    return () => motionQuery.revert();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      const account = await login(username.trim(), password);
      navigate(account.role === 'admin' ? '/dashboard' : '/prediksi');
    } catch (err) {
      const isNetworkError = !err.response;
      setError(
        isNetworkError
          ? 'Server ProdiPath belum terhubung. Jalankan backend dan pastikan MySQL aktif, lalu coba lagi.'
          : err.response?.data?.detail || 'Username atau password tidak sesuai.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main ref={pageRef} className="landing-page relative isolate min-h-screen overflow-hidden bg-slate-950 text-white">
      <div
        aria-hidden="true"
        className="landing-background"
        style={{ backgroundImage: "url('/landing-background.jpe')" }}
      />
      <div aria-hidden="true" className="landing-mesh-gradient">
        <div className="mesh-blob mesh-blob--blue" />
        <div className="mesh-blob mesh-blob--cyan" />
        <div className="mesh-blob mesh-blob--violet" />
        <div className="mesh-blob mesh-blob--sky" />
      </div>
      <div aria-hidden="true" className="landing-overlay" />
      <nav data-auto-reveal className="landing-nav relative z-10 mx-auto flex max-w-7xl items-center justify-between px-5 py-4 sm:px-8 sm:py-5">
        <Link to="/" className="flex items-center gap-3" aria-label="ProdiPath beranda">
          <span className="landing-brand-mark flex h-12 w-12 items-center justify-center overflow-hidden rounded-2xl bg-white p-1 shadow-lg shadow-blue-950/20">
            <img src="/sma-m2-logo.png" alt="Logo SMA Muhammadiyah 2 Bandar Lampung" className="h-full w-full object-contain" />
          </span>
          <span>
            <span className="block text-xl font-extrabold tracking-tight">ProdiPath</span>
            <span className="hidden text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-300 sm:block">SMA Muhammadiyah 2 Bandar Lampung</span>
          </span>
        </Link>
        <Link to="/prediksi" className="landing-cta inline-flex items-center gap-2 rounded-full border border-white/25 px-4 py-2.5 text-sm font-bold text-white transition">
          Coba rekomendasi <ArrowRight size={16} />
        </Link>
      </nav>

      <div className="landing-content relative z-10 mx-auto grid max-w-7xl items-center gap-10 px-6 py-9 sm:gap-12 sm:px-10 lg:min-h-[calc(100svh-156px)] lg:grid-cols-[1.12fr_0.88fr] lg:gap-16 lg:px-12 lg:py-8">
        <section className="landing-copy max-w-2xl">
          <div data-auto-reveal className="landing-eyebrow mb-7 inline-flex items-center gap-2 rounded-full border px-4 py-2.5 text-xs font-bold sm:text-sm">
            <Sparkles size={16} /> Untuk siswa kelas XII SMA Muhammadiyah 2 Bandar Lampung
          </div>
          <h1 data-auto-reveal className="text-4xl font-black leading-[1.06] tracking-tight sm:text-5xl lg:text-[3.45rem]">
            Sedang mencari
            <span className="landing-headline-accent block">jurusan kuliah?</span>
          </h1>
          <p data-auto-reveal className="mt-6 max-w-xl text-base leading-7 text-slate-200 sm:text-lg sm:leading-8">
            Isi profil singkatmu untuk melihat jurusan yang bisa kamu pertimbangkan, berdasarkan nilai dan minatmu.
          </p>

          <div className="mt-9 grid gap-4 sm:grid-cols-3">
            {[
              ['01', 'Isi data dan nilai'],
              ['02', 'Pilih minatmu'],
              ['03', 'Lihat pilihan jurusan'],
            ].map(([number, label]) => (
              <div data-auto-reveal key={number} className="landing-step rounded-2xl border p-4">
                <div className="landing-step-number flex h-8 w-8 items-center justify-center rounded-lg text-xs font-extrabold">{number}</div>
                <p className="mt-3 text-sm font-semibold text-white">{label}</p>
              </div>
            ))}
          </div>

          <p data-auto-reveal className="landing-disclaimer mt-7 flex items-start gap-2 text-xs leading-6 text-slate-200 sm:text-sm">
            <BookOpenCheck size={18} className="mt-0.5 shrink-0 text-amber-300" />
            Hasilnya sekadar bahan pertimbangan. Tetap cari tahu tentang jurusan dan kampus yang kamu minati.
          </p>
        </section>

        <section data-auto-reveal className="landing-login rounded-3xl p-7 text-slate-900 sm:p-9 lg:p-10">
          <div className="mb-7">
            <p className="landing-login-kicker text-xs font-extrabold uppercase tracking-[0.2em]">Area pengelola</p>
            <h2 className="mt-2 text-2xl font-extrabold tracking-tight">Masuk untuk mengelola data</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Halaman ini khusus untuk pengelola sekolah. Siswa bisa langsung mencoba rekomendasi tanpa masuk.
            </p>
          </div>

          {error && (
            <div role="alert" className="mb-5 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              <AlertCircle size={18} className="mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="username" className="mb-2 block text-sm font-semibold text-slate-700">Username</label>
              <input
                id="username"
                autoComplete="username"
                required
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                className="landing-input w-full rounded-xl border px-4 py-3.5 outline-none transition"
                placeholder="Masukkan username"
              />
            </div>
            <div>
              <label htmlFor="password" className="mb-2 block text-sm font-semibold text-slate-700">Password</label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="landing-input w-full rounded-xl border px-4 py-3.5 outline-none transition"
                placeholder="Masukkan password"
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="landing-submit flex w-full items-center justify-center gap-2 rounded-xl py-3.5 font-bold text-white transition disabled:cursor-wait disabled:opacity-60"
            >
              {submitting ? 'Memeriksa akun...' : 'Masuk ke dashboard'}
              {!submitting && <ArrowRight size={18} />}
            </button>
          </form>

          <div className="mt-6 border-t border-slate-100 pt-5 text-center text-sm text-slate-600">
            Ingin mencoba sebagai siswa?{' '}
            <Link to="/prediksi" className="font-bold text-blue-700 hover:text-blue-900">
              Isi profil di sini
            </Link>
          </div>
        </section>
      </div>

      <footer data-auto-reveal className="landing-footer relative z-10 border-t border-white/10 px-6 py-5 text-center text-xs text-slate-400">
        ProdiPath · Eksplorasi jurusan untuk siswa SMA Muhammadiyah 2 Bandar Lampung
      </footer>
    </main>
  );
}
