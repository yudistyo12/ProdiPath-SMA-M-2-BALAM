import { useEffect, useState } from 'react';
import { Bar, Doughnut } from 'react-chartjs-2';
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from 'chart.js';
import { ArrowRight, BookOpen, Database, GraduationCap, ListChecks, Sparkles, Upload, Users } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../utils/api';

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend);

const scoreLabels = {
  nilai_matematika: 'Matematika',
  nilai_sains: 'Sains',
  nilai_sosial: 'Sosial',
  nilai_bahasa: 'Bahasa',
};

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/dashboard/summary')
      .then((response) => setSummary(response.data))
      .catch((err) => setError(err.response?.data?.detail || 'Gagal memuat ringkasan. Pastikan backend dan database aktif.'));
  }, []);

  if (error) {
    return <div role="alert" className="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{error}</div>;
  }
  if (!summary) {
    return <div className="flex h-64 items-center justify-center text-sm text-slate-500">Memuat ringkasan data siswa...</div>;
  }

  const recommendations = summary.distribusi_rekomendasi || {};
  const tracks = summary.distribusi_jurusan_sma || {};
  const webRecommendations = summary.distribusi_rekomendasi_web || {};
  const webTracks = summary.distribusi_jurusan_sma_web || {};
  const totalTrackCategories = new Set([...Object.keys(tracks), ...Object.keys(webTracks)]).size;
  const totalRecommendationCategories = new Set([
    ...Object.keys(recommendations),
    ...Object.keys(webRecommendations),
  ]).size;
  const recommendationLabels = Object.keys(recommendations);
  const palette = ['#047857', '#ca8a04', '#0f766e', '#65a30d', '#d97706', '#14b8a6', '#a16207'];
  const totalRecords = Number(summary.total_siswa || 0) + Number(summary.total_pengisian_web || 0);
  const webShare = totalRecords > 0
    ? Math.round((Number(summary.total_pengisian_web || 0) / totalRecords) * 100)
    : 0;

  const recommendationChart = {
    labels: recommendationLabels,
    datasets: [{
      data: Object.values(recommendations),
      backgroundColor: recommendationLabels.map((_, index) => palette[index % palette.length]),
      borderWidth: 0,
    }],
  };
  const averageScores = summary.rata_rata_nilai || {};
  const scoreChart = {
    labels: Object.keys(scoreLabels).map((key) => scoreLabels[key]),
    datasets: [{
      label: 'Nilai rata-rata',
      data: Object.keys(scoreLabels).map((key) => averageScores[key] || 0),
      backgroundColor: '#059669',
      borderRadius: 7,
    }],
  };
  const webRecommendationLabels = Object.keys(webRecommendations);
  const webAverageScores = summary.rata_rata_nilai_web || {};
  const getTopEntry = (distribution) => Object.entries(distribution)
    .sort((first, second) => second[1] - first[1] || first[0].localeCompare(second[0]))[0] || null;
  const topWebRecommendation = getTopEntry(webRecommendations);
  const topCsvRecommendation = getTopEntry(recommendations);
  const topWebTrack = getTopEntry(webTracks);
  const topCsvTrack = getTopEntry(tracks);
  const webScoreChart = {
    labels: Object.keys(scoreLabels).map((key) => scoreLabels[key]),
    datasets: [{
      label: 'Nilai rata-rata',
      data: Object.keys(scoreLabels).map((key) => webAverageScores[key] || 0),
      backgroundColor: '#0f766e',
      borderRadius: 7,
    }],
  };

  return (
    <div className="dashboard-page space-y-7">
      <section className="dashboard-hero relative overflow-hidden rounded-3xl p-7 text-white sm:p-9">
        <div className="dashboard-hero-orb dashboard-hero-orb-one" aria-hidden="true" />
        <div className="dashboard-hero-orb dashboard-hero-orb-two" aria-hidden="true" />
        <div className="relative z-10 flex flex-col justify-between gap-6 lg:flex-row lg:items-end">
          <div className="max-w-2xl">
            <p className="flex items-center gap-2 text-sm font-bold text-emerald-200">
              <Sparkles size={16} /> Ringkasan ProdiPath
            </p>
            <h2 className="mt-3 text-3xl font-black tracking-tight sm:text-4xl">Data siswa dalam satu tempat.</h2>
            <p className="mt-3 max-w-xl text-sm leading-6 text-slate-200">
              Pantau data yang diimpor sekolah dan jawaban yang dikirim siswa melalui form.
            </p>
          </div>
          <Link to="/import" className="dashboard-primary-button inline-flex shrink-0 items-center justify-center gap-2 rounded-xl px-5 py-3 text-sm font-bold transition">
            <Database size={17} /> Kelola dataset <ArrowRight size={17} />
          </Link>
        </div>
      </section>

      <section className="dashboard-stat-grid grid gap-4">
        <StatCard icon={Database} label="Data latih CSV" description="Data yang diimpor sekolah" value={summary.total_siswa} color="green" />
        <StatCard icon={Users} label="Pengisian melalui web" description="Jawaban siswa tersimpan" value={summary.total_pengisian_web} color="teal" />
        <StatCard icon={BookOpen} label="Peminatan SMA" description="Jenis peminatan tercatat" value={totalTrackCategories} color="gold" />
        <StatCard icon={GraduationCap} label="Pilihan jurusan" description="Jenis rekomendasi tercatat" value={totalRecommendationCategories} color="olive" />
      </section>

      <section className="dashboard-card rounded-2xl p-5 sm:p-6">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h3 className="font-bold text-slate-900">Sumber data</h3>
            <p className="mt-1 text-sm text-slate-500">
              {totalRecords.toLocaleString('id-ID')} data tercatat; masing-masing sumber tetap dipisahkan.
            </p>
          </div>
          <div className="flex flex-wrap gap-4 text-sm">
            <span className="inline-flex items-center gap-2 font-semibold text-slate-700">
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-600" />
              CSV · {Number(summary.total_siswa || 0).toLocaleString('id-ID')}
            </span>
            <span className="inline-flex items-center gap-2 font-semibold text-slate-700">
              <span className="h-2.5 w-2.5 rounded-full bg-amber-500" />
              Web · {Number(summary.total_pengisian_web || 0).toLocaleString('id-ID')}
            </span>
          </div>
        </div>
        <div className="dashboard-source-track mt-4" aria-label={`${webShare}% data berasal dari pengisian web`}>
          <div className="dashboard-source-csv" style={{ width: `${100 - webShare}%` }} />
          <div className="dashboard-source-web" style={{ width: `${webShare}%` }} />
        </div>
      </section>

      <section className="dashboard-overview-grid grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="dashboard-card rounded-2xl p-5 sm:p-6">
          <div className="mb-5 flex items-start gap-3">
            <span className="dashboard-panel-icon flex h-10 w-10 shrink-0 items-center justify-center rounded-xl">
              <ListChecks size={20} />
            </span>
            <div>
              <h3 className="font-bold text-slate-900">Ringkasan pilihan</h3>
              <p className="mt-1 text-sm text-slate-500">Pilihan yang paling sering muncul di tiap sumber data.</p>
            </div>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <InsightCard
              label="Rekomendasi web terbanyak"
              entry={topWebRecommendation}
              sourceCount={summary.total_pengisian_web}
              emptyText="Belum ada jawaban dari form web."
              tone="green"
            />
            <InsightCard
              label="Rekomendasi CSV terbanyak"
              entry={topCsvRecommendation}
              sourceCount={summary.total_siswa}
              emptyText="Dataset CSV belum diimpor."
              tone="gold"
            />
            <InsightCard
              label="Peminatan web terbanyak"
              entry={topWebTrack}
              sourceCount={summary.total_pengisian_web}
              emptyText="Belum ada data peminatan dari form web."
              tone="teal"
            />
            <InsightCard
              label="Peminatan CSV terbanyak"
              entry={topCsvTrack}
              sourceCount={summary.total_siswa}
              emptyText="Belum ada data peminatan dari CSV."
              tone="olive"
            />
          </div>
        </div>

        <div className="dashboard-card rounded-2xl p-5 sm:p-6">
          <div className="mb-5">
            <h3 className="font-bold text-slate-900">Akses cepat</h3>
            <p className="mt-1 text-sm text-slate-500">Buka bagian yang ingin kamu kelola.</p>
          </div>
          <div className="space-y-3">
            <QuickLink
              to="/mahasiswa"
              icon={Users}
              title="Lihat data siswa"
              description="Cari nama, NISN, dan hasil rekomendasi."
              tone="green"
            />
            <QuickLink
              to="/import"
              icon={Upload}
              title="Impor dataset"
              description="Tambahkan atau perbarui data dari CSV."
              tone="gold"
            />
            <QuickLink
              to="/prediksi"
              icon={ArrowRight}
              title="Buka form rekomendasi"
              description="Lihat halaman yang digunakan siswa."
              tone="teal"
            />
          </div>
          <div className="dashboard-access-note mt-5 rounded-xl px-4 py-3 text-xs leading-5">
            Data pengisian web dan dataset CSV ditampilkan terpisah agar sumbernya mudah dibedakan.
          </div>
        </div>
      </section>

      <section className="dashboard-card rounded-2xl p-5 sm:p-6">
        <div className="mb-5">
          <h3 className="font-bold text-slate-900">Sebaran data lebih rinci</h3>
          <p className="mt-1 text-sm text-slate-500">
            Bandingkan peminatan dan rekomendasi berdasarkan sumber datanya.
          </p>
        </div>
        <div className="grid gap-6 xl:grid-cols-2">
          <DistributionComparison
            title="Peminatan SMA"
            firstLabel="Dataset CSV"
            firstDistribution={tracks}
            firstTotal={summary.total_siswa}
            secondLabel="Pengisian web"
            secondDistribution={webTracks}
            secondTotal={summary.total_pengisian_web}
          />
          <DistributionComparison
            title="Jurusan rekomendasi"
            firstLabel="Dataset CSV"
            firstDistribution={recommendations}
            firstTotal={summary.total_siswa}
            secondLabel="Pengisian web"
            secondDistribution={webRecommendations}
            secondTotal={summary.total_pengisian_web}
          />
        </div>
      </section>

      {summary.total_siswa === 0 ? (
        <section className="dashboard-empty rounded-2xl p-7 sm:p-9">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-700">
            <Database size={22} />
          </div>
          <h3 className="mt-4 font-bold text-slate-900">Dataset sekolah belum diimpor</h3>
          <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-slate-600">
            Pengisian web sudah tercatat terpisah. Impor dataset sekolah jika ingin melihat ringkasan data latih dan distribusi labelnya.
          </p>
          <Link to="/import" className="dashboard-text-link mt-4 inline-flex items-center gap-1 font-bold">
            Impor dataset <ArrowRight size={16} />
          </Link>
        </section>
      ) : (
        <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <div className="dashboard-card rounded-2xl p-5 sm:p-7">
            <div className="mb-5">
              <h3 className="text-lg font-bold text-slate-900">Jurusan pada data latih</h3>
              <p className="mt-1 text-sm text-slate-500">Jumlah data CSV untuk setiap jurusan rujukan.</p>
            </div>
            <div className="h-[340px]">
              <Bar
                data={recommendationChart}
                options={{
                  indexAxis: 'y',
                  maintainAspectRatio: false,
                  plugins: { legend: { display: false } },
                  scales: {
                    x: { beginAtZero: true, ticks: { precision: 0, color: '#64748b' }, grid: { color: '#edf2ef' } },
                    y: { ticks: { color: '#475569' }, grid: { display: false } },
                  },
                }}
              />
            </div>
          </div>

          <div className="dashboard-card rounded-2xl p-5 sm:p-7">
            <h3 className="text-lg font-bold text-slate-900">Asal jurusan SMA</h3>
            <p className="mt-1 text-sm text-slate-500">Komposisi siswa berdasarkan peminatan saat SMA.</p>
            <div className="mx-auto mt-6 h-64 max-w-[300px]">
              <Doughnut
                data={{
                  labels: Object.keys(tracks),
                  datasets: [{
                    data: Object.values(tracks),
                    backgroundColor: ['#047857', '#ca8a04', '#65a30d'],
                    hoverOffset: 7,
                    borderWidth: 0,
                  }],
                }}
                options={{
                  maintainAspectRatio: false,
                  cutout: '70%',
                  plugins: { legend: { position: 'bottom', labels: { usePointStyle: true, pointStyle: 'circle', padding: 18, color: '#475569' } } },
                }}
              />
            </div>
            <div className="mt-5 border-t border-slate-100 pt-5">
              <p className="mb-3 text-sm font-bold text-slate-700">Rata-rata nilai akademik</p>
              <div className="h-36">
                <Bar
                  data={scoreChart}
                  options={{
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                      y: { min: 0, max: 100, ticks: { color: '#64748b' }, grid: { color: '#edf2ef' } },
                      x: { ticks: { color: '#475569' }, grid: { display: false } },
                    },
                  }}
                />
              </div>
            </div>
          </div>
        </section>
      )}

      {summary.total_pengisian_web > 0 && (
        <section>
          <div className="mb-5">
            <h3 className="text-xl font-black text-slate-900">Jawaban yang dikirim melalui web</h3>
            <p className="mt-1 text-sm text-slate-500">
              Ringkasan ini hanya memakai pengisian web, tidak dicampur dengan data latih CSV.
            </p>
          </div>
          <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
            <div className="dashboard-card rounded-2xl p-5 sm:p-7">
              <div className="mb-5">
                <h4 className="text-lg font-bold text-slate-900">Distribusi hasil rekomendasi</h4>
                <p className="mt-1 text-sm text-slate-500">Jumlah hasil rekomendasi dari pengisian web.</p>
              </div>
              <div className="h-[340px]">
                <Bar
                  data={{
                    labels: webRecommendationLabels,
                    datasets: [{
                      data: Object.values(webRecommendations),
                      backgroundColor: webRecommendationLabels.map((_, index) => palette[index % palette.length]),
                      borderWidth: 0,
                    }],
                  }}
                  options={{
                    indexAxis: 'y',
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                      x: { beginAtZero: true, ticks: { precision: 0, color: '#64748b' }, grid: { color: '#edf2ef' } },
                      y: { ticks: { color: '#475569' }, grid: { display: false } },
                    },
                  }}
                />
              </div>
            </div>

            <div className="dashboard-card rounded-2xl p-5 sm:p-7">
              <h4 className="text-lg font-bold text-slate-900">Asal jurusan SMA</h4>
              <p className="mt-1 text-sm text-slate-500">Komposisi pengisi kuesioner web.</p>
              <div className="mx-auto mt-6 h-64 max-w-[300px]">
                <Doughnut
                  data={{
                    labels: Object.keys(webTracks),
                    datasets: [{
                      data: Object.values(webTracks),
                      backgroundColor: ['#047857', '#ca8a04', '#65a30d'],
                      hoverOffset: 7,
                      borderWidth: 0,
                    }],
                  }}
                  options={{
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: { legend: { position: 'bottom', labels: { usePointStyle: true, pointStyle: 'circle', padding: 18, color: '#475569' } } },
                  }}
                />
              </div>
              <div className="mt-5 border-t border-slate-100 pt-5">
                <p className="mb-3 text-sm font-bold text-slate-700">Rata-rata nilai akademik</p>
                <div className="h-36">
                  <Bar
                    data={webScoreChart}
                    options={{
                      maintainAspectRatio: false,
                      plugins: { legend: { display: false } },
                      scales: {
                        y: { min: 0, max: 100, ticks: { color: '#64748b' }, grid: { color: '#edf2ef' } },
                        x: { ticks: { color: '#475569' }, grid: { display: false } },
                      },
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      <p className="dashboard-footnote rounded-xl px-4 py-3 text-xs leading-5">
        Ringkasan ini menunjukkan data yang tersedia. Rekomendasi merupakan bahan pertimbangan, bukan ukuran keberhasilan atau jaminan pilihan kuliah.
      </p>
    </div>
  );
}

function StatCard({ icon: Icon, label, description, value, color }) {
  const colors = {
    green: 'dashboard-stat-icon-green',
    teal: 'dashboard-stat-icon-teal',
    gold: 'dashboard-stat-icon-gold',
    olive: 'dashboard-stat-icon-olive',
  };

  return (
    <div className="dashboard-stat-card flex items-center justify-between rounded-2xl p-5">
      <div className="min-w-0">
        <p className="text-sm font-semibold text-slate-600">{label}</p>
        <p className="mt-1 text-xs text-slate-500">{description}</p>
        <p className="mt-3 text-3xl font-black tracking-tight text-slate-950">{Number(value || 0).toLocaleString('id-ID')}</p>
      </div>
      <div className={`dashboard-stat-icon flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl ${colors[color]}`}>
        <Icon size={23} />
      </div>
    </div>
  );
}

function InsightCard({ label, entry, sourceCount, emptyText, tone }) {
  const tones = {
    green: 'dashboard-insight-green',
    gold: 'dashboard-insight-gold',
    teal: 'dashboard-insight-teal',
    olive: 'dashboard-insight-olive',
  };

  return (
    <div className={`dashboard-insight-card rounded-xl p-4 ${tones[tone]}`}>
      <p className="text-xs font-semibold text-slate-600">{label}</p>
      {entry ? (
        <>
          <p className="mt-2 truncate text-lg font-extrabold text-slate-900" title={entry[0]}>{entry[0]}</p>
          <p className="mt-1 text-xs text-slate-600">
            {Number(entry[1]).toLocaleString('id-ID')} dari {Number(sourceCount || 0).toLocaleString('id-ID')} data
          </p>
        </>
      ) : (
        <p className="mt-3 text-sm leading-5 text-slate-600">{emptyText}</p>
      )}
    </div>
  );
}

function QuickLink({ to, icon: Icon, title, description, tone }) {
  const tones = {
    green: 'dashboard-quick-icon-green',
    gold: 'dashboard-quick-icon-gold',
    teal: 'dashboard-quick-icon-teal',
  };

  return (
    <Link to={to} className="dashboard-quick-link flex items-center gap-3 rounded-xl border border-slate-200 p-3.5 transition">
      <span className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${tones[tone]}`}>
        <Icon size={19} />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block text-sm font-bold text-slate-800">{title}</span>
        <span className="mt-0.5 block text-xs leading-5 text-slate-500">{description}</span>
      </span>
      <ArrowRight size={16} className="shrink-0 text-slate-400" />
    </Link>
  );
}

function DistributionComparison({
  title,
  firstLabel,
  firstDistribution,
  firstTotal,
  secondLabel,
  secondDistribution,
  secondTotal,
}) {
  const categories = [...new Set([
    ...Object.keys(firstDistribution),
    ...Object.keys(secondDistribution),
  ])].sort((first, second) => first.localeCompare(second, 'id'));

  return (
    <div className="dashboard-distribution rounded-xl p-4 sm:p-5">
      <div className="mb-4 flex items-center justify-between gap-3">
        <h4 className="text-sm font-bold text-slate-800">{title}</h4>
        <div className="flex flex-wrap justify-end gap-x-3 gap-y-1 text-[11px] font-semibold text-slate-500">
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-emerald-700" /> CSV
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-amber-500" /> Web
          </span>
        </div>
      </div>
      {categories.length > 0 ? (
        <div className="space-y-4">
          {categories.map((category) => {
            const firstCount = Number(firstDistribution[category] || 0);
            const secondCount = Number(secondDistribution[category] || 0);
            const firstPercent = firstTotal ? Math.round((firstCount / firstTotal) * 100) : 0;
            const secondPercent = secondTotal ? Math.round((secondCount / secondTotal) * 100) : 0;

            return (
              <div key={category} className="dashboard-distribution-row">
                <div className="mb-2 flex items-center justify-between gap-3">
                  <span className="truncate text-sm font-semibold text-slate-700" title={category}>{category}</span>
                  <span className="shrink-0 text-[11px] text-slate-500">
                    {firstCount + secondCount} data
                  </span>
                </div>
                <DistributionBar label={firstLabel} count={firstCount} percent={firstPercent} source="csv" />
                <DistributionBar label={secondLabel} count={secondCount} percent={secondPercent} source="web" />
              </div>
            );
          })}
        </div>
      ) : (
        <div className="dashboard-distribution-empty flex min-h-32 items-center justify-center rounded-lg px-5 text-center text-sm text-slate-500">
          Data sebaran akan muncul setelah ada data siswa.
        </div>
      )}
    </div>
  );
}

function DistributionBar({ label, count, percent, source }) {
  return (
    <div className="grid grid-cols-[82px_minmax(0,1fr)_56px] items-center gap-2">
      <span className="text-[10px] font-medium text-slate-500">{label}</span>
      <div className="dashboard-distribution-track">
        <div
          className={`dashboard-distribution-fill dashboard-distribution-fill-${source}`}
          style={{ width: `${percent}%` }}
        />
      </div>
      <span className="text-right text-[10px] font-semibold tabular-nums text-slate-600">
        {count} · {percent}%
      </span>
    </div>
  );
}
