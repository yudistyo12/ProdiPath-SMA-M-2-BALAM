import { useState } from 'react';
import { AlertCircle, CheckCircle2, Download, FileSpreadsheet, UploadCloud } from 'lucide-react';
import api from '../utils/api';

const templateHeader = [
  'nisn',
  'nama',
  'jurusan_sma',
  'nilai_matematika',
  'nilai_sains',
  'nilai_sosial',
  'nilai_bahasa',
  'minat_teknologi',
  'minat_seni',
  'minat_komunikasi',
  'kemampuan_analitis',
  'rekomendasi_jurusan',
];

export default function ImportData() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];
    setResult(null);
    if (selectedFile && selectedFile.name.toLowerCase().endsWith('.csv')) {
      setFile(selectedFile);
      setError('');
    } else {
      setFile(null);
      setError('Pilih file dengan ekstensi .csv.');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Pilih file CSV terlebih dahulu.');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/dataset/import', formData);
      setResult(response.data);
      setFile(null);
      const input = document.getElementById('file-upload');
      if (input) input.value = '';
    } catch (err) {
      setError(err.response?.data?.detail || 'Dataset gagal diunggah. Periksa koneksi backend.');
    } finally {
      setLoading(false);
    }
  };

  const downloadTemplate = () => {
    const content = `${templateHeader.join(',')}\n`;
    const url = URL.createObjectURL(new Blob([content], { type: 'text/csv;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = 'template_dataset_rekomendasi_jurusan.csv';
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <section>
        <p className="text-sm font-semibold text-blue-700">Data untuk pelatihan dan analisis</p>
        <h2 className="mt-1 text-2xl font-black text-slate-900">Dataset siswa kelas XII</h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
          Impor data akademik, minat, dan label rekomendasi jurusan. Data dengan NISN yang sama akan diperbarui.
        </p>
      </section>

      <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-8">
        <div className="mb-6 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
          <div>
            <h3 className="font-bold text-slate-900">Unggah file CSV</h3>
            <p className="mt-1 text-sm text-slate-500">Pastikan kolom dan nilai sudah mengikuti template.</p>
          </div>
          <button
            type="button"
            onClick={downloadTemplate}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-bold text-slate-700 transition hover:bg-slate-50"
          >
            <Download size={17} /> Unduh template
          </button>
        </div>

        <label
          htmlFor="file-upload"
          className="flex min-h-52 cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-300 bg-slate-50/60 px-5 py-8 text-center transition hover:border-blue-400 hover:bg-blue-50/40"
        >
          <input id="file-upload" type="file" accept=".csv,text/csv" className="sr-only" onChange={handleFileChange} />
          <span className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-100 text-blue-700">
            {file ? <FileSpreadsheet size={27} /> : <UploadCloud size={28} />}
          </span>
          {file ? (
            <>
              <span className="font-bold text-slate-800">{file.name}</span>
              <span className="mt-1 text-sm text-slate-500">{(file.size / 1024).toFixed(1)} KB · Klik untuk mengganti file</span>
            </>
          ) : (
            <>
              <span className="font-bold text-slate-800">Klik untuk memilih file CSV</span>
              <span className="mt-1 text-sm text-slate-500">Format data siswa dan label rekomendasi</span>
            </>
          )}
        </label>

        {error && (
          <div role="alert" className="mt-5 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            <AlertCircle size={18} className="mt-0.5 shrink-0" /> {error}
          </div>
        )}
        {result && (
          <div className="mt-5 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">
            <div className="flex items-center gap-2 font-bold"><CheckCircle2 size={18} /> {result.message}</div>
            {result.errors?.length > 0 && (
              <div className="mt-3">
                <p className="font-semibold">Baris yang perlu diperiksa:</p>
                <ul className="mt-1 max-h-32 list-inside list-disc space-y-1 overflow-y-auto text-emerald-900/80">
                  {result.errors.map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}
                </ul>
              </div>
            )}
          </div>
        )}

        <button
          type="button"
          onClick={handleUpload}
          disabled={!file || loading}
          className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3.5 font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          {loading ? 'Mengimpor data...' : 'Unggah dan simpan dataset'}
        </button>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-5">
        <h3 className="text-sm font-bold text-slate-800">Ketentuan kolom</h3>
        <ul className="mt-3 grid gap-x-8 gap-y-2 text-sm leading-6 text-slate-600 sm:grid-cols-2">
          <li><code className="text-slate-800">nisn, nama</code> harus terisi.</li>
          <li><code className="text-slate-800">jurusan_sma</code>: IPA, IPS, atau Bahasa.</li>
          <li>Nilai akademik: bilangan bulat 0–100.</li>
          <li>Minat dan kemampuan analitis: bilangan bulat 1–5.</li>
          <li><code className="text-slate-800">rekomendasi_jurusan</code> adalah label contoh/hasil rujukan.</li>
        </ul>
      </section>
    </div>
  );
}
