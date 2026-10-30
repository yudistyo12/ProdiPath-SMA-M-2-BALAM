# ProdiPath

**ProdiPath** adalah prototipe website sistem rekomendasi jurusan kuliah untuk siswa kelas XII SMA Muhammadiyah 2 Bandar Lampung. Sistem membantu siswa mengeksplorasi pilihan studi dengan membandingkan profil akademik, minat, dan kemampuan analitis terhadap contoh data yang tersedia.

Sasaran pengguna proyek adalah siswa kelas XII SMA Muhammadiyah 2 Bandar Lampung. Kebutuhan dan prosedur penerapan di sekolah tetap perlu dikonfirmasi bersama pihak sekolah/guru BK.

Rekomendasi merupakan **bahan pertimbangan awal**, bukan penilaian pasti tentang kemampuan siswa, jaminan diterima di perguruan tinggi, atau pengganti konsultasi dengan guru BK, orang tua, dan informasi resmi kampus.

## Konsep dan alur

1. Siswa mengisi nama, NISN, peminatan/jurusan SMA, serta nilai Matematika, Sains, Sosial, dan Bahasa.
2. Siswa mengisi skala minat Teknologi, Seni, Komunikasi, dan kemampuan Analitis, lalu menyetujui penyimpanan data.
3. Backend mengirim profil ke model **Decision Tree** yang dilatih dari dataset berlabel `rekomendasi_jurusan`.
4. Website menampilkan satu rekomendasi jurusan untuk dieksplorasi lebih lanjut dan menyimpan profil serta hasilnya pada database.
5. Administrator dapat mengimpor dataset, melihat ringkasan distribusi data, serta meninjau dan menghapus data siswa.

Pengisian melalui web disimpan dengan sumber `kuesioner_web`; impor CSV disimpan dengan sumber `dataset`. Ringkasan distribusi model hanya menggunakan label dari data latih CSV, tidak mencampur hasil prediksi web sebagai label kebenaran. Data pengisian web dengan NISN yang sama memperbarui entri sebelumnya. Persetujuan penyimpanan dicatat bersama jawaban web. Persetujuan dan penggunaan data harus disampaikan dengan jelas kepada siswa sesuai arahan sekolah sebelum formulir digunakan.

## Fitur

- Halaman beranda yang menjelaskan tujuan sistem dan menyediakan login pengelola.
- Form rekomendasi jurusan yang dapat digunakan tanpa login.
- Dashboard distribusi jurusan rekomendasi dan jurusan SMA pada dataset.
- Daftar dan pencarian data siswa untuk administrator.
- Import CSV dengan validasi kolom dan rentang nilai.
- Model machine learning dengan fitur jurusan SMA, nilai akademik, minat, dan kemampuan analitis.

## Teknologi

- **Frontend:** React, Vite, Tailwind CSS, Chart.js.
- **Backend:** Python, FastAPI, pandas, scikit-learn.
- **Database:** MySQL.
- **Model:** Decision Tree Classifier dengan encoding kategori jurusan SMA.

## Format dataset

File `data/questionnaire_real.csv` menjadi dataset contoh. Header CSV yang digunakan:

```csv
nisn,nama,jurusan_sma,nilai_matematika,nilai_sains,nilai_sosial,nilai_bahasa,minat_teknologi,minat_seni,minat_komunikasi,kemampuan_analitis,rekomendasi_jurusan
```

- `jurusan_sma`: `IPA`, `IPS`, atau `Bahasa`.
- Nilai akademik: bilangan bulat 0–100.
- Minat dan kemampuan analitis: bilangan bulat 1–5.
- `rekomendasi_jurusan`: label jurusan rujukan untuk pelatihan model.
- `nisn` disimpan sebagai teks agar angka nol di depan tidak hilang.
- Pengisian web mensyaratkan NISN 10 digit, nama, serta persetujuan penyimpanan data.

Dataset contoh yang kecil dan label yang tersebar pada banyak jurusan **belum memadai untuk menyimpulkan akurasi atau kelayakan rekomendasi di dunia nyata**. Kumpulkan data yang cukup, seimbang, representatif, dan berizin; evaluasi model pada data yang tidak digunakan saat pelatihan sebelum membuat klaim akurasi.

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
python ml\train.py
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

## Melatih ulang model

Setelah dataset diperbarui, jalankan dari folder proyek:

```powershell
python ml\train.py
```

Model tersimpan di `models/model_jurusan.pkl`, dengan encoder label di `models/label_encoder.pkl`. Skrip menampilkan akurasi holdout sebagai gambaran awal saja; pada dataset kecil atau kelas yang jarang, nilai ini sangat tidak stabil dan bukan bukti akurasi umum model.

### Mencoba training dengan data sintetis

`data/questionnaire_synthetic_demo.csv` berisi data buatan untuk mencoba alur training. Data ini bukan data siswa sungguhan, tidak boleh dipakai untuk menyimpulkan akurasi atau membuat rekomendasi nyata, dan tidak cocok diimpor sebagai data siswa ke dashboard.

Untuk menguji training tanpa menimpa model yang dipakai aplikasi:

```powershell
python ml\train.py --data data\questionnaire_synthetic_demo.csv --output-dir models\demo
```

File hasil uji tersimpan terpisah di `models/demo`. Aplikasi tetap menggunakan model di `models`.

## Endpoint utama

- `POST /api/predict/` — menghasilkan rekomendasi dari profil akademik dan minat.
- `POST /api/auth/login`, `GET /api/auth/me` — autentikasi administrator.
- `GET /api/dashboard/summary` — ringkasan dataset untuk dashboard.
- `GET /api/students/`, `GET /api/students/{nisn}`, `DELETE /api/students/{nisn}` — pengelolaan data siswa.
- `POST /api/dataset/import` — impor data CSV.
