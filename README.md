# ProdiPath

**ProdiPath** adalah prototipe sistem pendukung keputusan (SPK) berbasis web untuk membantu siswa kelas XII SMA Muhammadiyah 2 Bandar Lampung mengeksplorasi pilihan program studi. Sistem menggunakan metode **Simple Additive Weighting (SAW)** untuk merangking alternatif program studi berdasarkan kesesuaian profil akademik, minat, dan peminatan SMA.

Sasaran pengguna proyek adalah siswa kelas XII SMA Muhammadiyah 2 Bandar Lampung. Kebutuhan dan prosedur penerapan di sekolah tetap perlu dikonfirmasi bersama pihak sekolah/guru BK.

Rekomendasi merupakan **bahan pertimbangan awal**, bukan penilaian pasti tentang kemampuan siswa, jaminan diterima di perguruan tinggi, atau pengganti konsultasi dengan guru BK, orang tua, dan informasi resmi kampus.

## Konsep dan alur

1. Siswa mengisi nama, NISN, peminatan/jurusan SMA, serta nilai Matematika, Sains, Sosial, dan Bahasa.
2. Siswa mengisi skala minat Teknologi, Seni, Komunikasi, dan kemampuan Analitis, lalu menyetujui penyimpanan data.
3. Backend mengambil data referensi berlabel `dataset` dari database dan membentuk profil rata-rata untuk setiap alternatif program studi.
4. Untuk setiap alternatif, sistem menghitung nilai kecocokan 0–100 pada 9 kriteria: peminatan SMA, empat nilai akademik, tiga minat, dan kemampuan analitis. Kecocokan numerik dihitung dari jarak terhadap profil rata-rata alternatif; kecocokan peminatan dihitung dari proporsi data referensi pada alternatif tersebut yang memiliki peminatan yang sama.
5. Sistem menerapkan SAW dengan bobot awal sama rata (1/9 per kriteria), menjumlahkan nilai kecocokan berbobot, lalu mengurutkan alternatif dari skor tertinggi.
6. Website menampilkan tiga alternatif teratas beserta skor dan jumlah data rujukan. Alternatif peringkat pertama disimpan sebagai rekomendasi utama bersama profil siswa.
7. Administrator dapat mengimpor dataset, melihat ringkasan distribusi data, serta meninjau dan menghapus data siswa.

Untuk kriteria numerik, nilai kecocokan adalah `max(0, 100 × (1 − |nilai siswa − rata-rata alternatif| / rentang kriteria))`, dengan rentang 100 untuk nilai akademik dan 4 untuk skala minat/analitis. Kesesuaian peminatan adalah persentase data referensi pada alternatif yang memiliki peminatan SMA sama. Skor akhir alternatif `i` adalah `V_i = Σ(w_j × r_ij)`; pada bobot awal sama rata, `w_j = 1/9`.

Pengisian melalui web disimpan dengan sumber `kuesioner_web`; impor CSV disimpan dengan sumber `dataset`. Hanya data bersumber `dataset` yang digunakan sebagai profil referensi SAW; hasil rekomendasi web tidak digunakan kembali sebagai data rujukan. Data pengisian web dengan NISN yang sama memperbarui entri sebelumnya. Persetujuan penyimpanan dicatat bersama jawaban web. Persetujuan dan penggunaan data harus disampaikan dengan jelas kepada siswa sesuai arahan sekolah sebelum formulir digunakan.

Bobot sama rata adalah **bobot awal prototipe**, bukan bobot yang telah disetujui sekolah. Kriteria, bobot, dan kelayakan data rujukan harus divalidasi bersama guru BK. Skor SAW menunjukkan kecocokan terhadap data rujukan, bukan peluang keberhasilan atau ukuran baku kemampuan siswa.

## Fitur

- Halaman beranda yang menjelaskan tujuan sistem dan menyediakan login pengelola.
- Form rekomendasi jurusan yang dapat digunakan tanpa login.
- Dashboard distribusi jurusan rekomendasi dan jurusan SMA pada dataset.
- Daftar dan pencarian data siswa untuk administrator.
- Import CSV dengan validasi kolom dan rentang nilai.
- Perangkingan alternatif program studi menggunakan metode SAW.

## Teknologi

- **Frontend:** React, Vite, Tailwind CSS, Chart.js.
- **Backend:** Python dan FastAPI.
- **Database:** MySQL.
- **Metode SPK:** Simple Additive Weighting (SAW), dengan bobot awal sama rata.

## Format dataset

File `data/questionnaire_real.csv` menjadi dataset contoh. Header CSV yang digunakan:

```csv
nisn,nama,jurusan_sma,nilai_matematika,nilai_sains,nilai_sosial,nilai_bahasa,minat_teknologi,minat_seni,minat_komunikasi,kemampuan_analitis,rekomendasi_jurusan
```

- `jurusan_sma`: `IPA`, `IPS`, atau `Bahasa`.
- Nilai akademik: bilangan bulat 0–100.
- Minat dan kemampuan analitis: bilangan bulat 1–5.
- `rekomendasi_jurusan`: nama alternatif program studi untuk pengelompokan profil referensi SAW.
- `nisn` disimpan sebagai teks agar angka nol di depan tidak hilang.
- Pengisian web mensyaratkan NISN 10 digit, nama, serta persetujuan penyimpanan data.

Dataset contoh saat ini berisi 25 baris untuk 17 alternatif program studi, sehingga banyak alternatif hanya memiliki sedikit data rujukan. Hasilnya **belum memadai untuk menyimpulkan kelayakan rekomendasi di dunia nyata**. Gunakan data yang cukup, representatif, dan berizin; validasi profil alternatif dan bobot kriteria bersama guru BK sebelum penggunaan nyata.

## Menyiapkan database

1. Jalankan MySQL, misalnya melalui XAMPP.
2. Untuk instalasi baru, jalankan `database/schema.sql`, lalu `database/seed.sql`.
3. Akun pengelola awal: username `admin`, password `admin123`. Ganti kredensial ini sebelum penggunaan nyata.
4. Backend saat ini tersambung ke database `metopen_db` dengan konfigurasi lokal `root` tanpa password di `backend/database.py`. Sesuaikan konfigurasi tersebut untuk lingkungan Anda.
5. Kunci token memakai variabel lingkungan `PRODIPATH_SECRET_KEY`. Nilai bawaan hanya untuk pengembangan lokal; tetapkan kunci acak rahasia sebelum deploy, misalnya di PowerShell: `$env:PRODIPATH_SECRET_KEY = (python -c "import secrets; print(secrets.token_urlsafe(48))")`.

`schema.sql` tidak menghapus tabel yang sudah ada. **Jika database berasal dari versi lama aplikasi** (tabel `questionnaire_data` masih memakai kolom `npm`, `program_studi`, atau `performa_belajar`), cadangkan database terlebih dahulu, lalu rename tabel lama agar datanya tetap tersimpan, misalnya:

```sql
USE metopen_db;
RENAME TABLE questionnaire_data TO questionnaire_data_legacy;
```

Setelah itu jalankan `database/schema.sql` dan `database/seed.sql`. Tabel lama tidak otomatis dikonversi karena kolom dan maknanya berbeda dari data siswa kelas XII.

## Menjalankan aplikasi

### Backend

```powershell
.\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
uvicorn backend.main:app --reload
```

Backend tersedia di `http://localhost:8000`; dokumentasi API FastAPI ada di `http://localhost:8000/docs`.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Buka URL yang ditampilkan Vite, biasanya `http://localhost:5173`. Jika backend berjalan di alamat berbeda, atur `VITE_API_URL`, misalnya `http://localhost:8000/api`.

Di Windows, `run.bat` dapat digunakan untuk membuka backend, frontend, dan browser. Pastikan dependensi sudah terpasang dan MySQL aktif.

## Memperbarui data referensi SAW

Administrator mengimpor CSV melalui fitur dataset. Data dengan sumber `dataset` akan menjadi dasar profil alternatif program studi pada perhitungan SAW. Pengisian kuesioner web tidak menjadi data referensi. Pastikan sumber, izin penggunaan, kualitas data, kecukupan jumlah baris per program studi, kriteria, dan bobot telah divalidasi oleh sekolah.

## Endpoint utama

- `POST /api/predict/` — menghasilkan rekomendasi dari profil akademik dan minat.
- `POST /api/auth/login`, `GET /api/auth/me` — autentikasi administrator.
- `GET /api/dashboard/summary` — ringkasan dataset untuk dashboard.
- `GET /api/students/`, `GET /api/students/{nisn}`, `DELETE /api/students/{nisn}` — pengelolaan data siswa.
- `POST /api/dataset/import` — impor data CSV.
