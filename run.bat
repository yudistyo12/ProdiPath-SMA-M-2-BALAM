@echo off
echo ===================================================
echo Memulai ProdiPath - Rekomendasi Jurusan...
echo ===================================================

echo [1/2] Menjalankan Server Backend FastAPI...
start cmd /k ".\venv\Scripts\activate && uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/3] Menjalankan Frontend React (Vite)...
start cmd /k "cd frontend && npm run dev"

echo [3/3] Membuka Frontend di Browser...
timeout /t 5 /nobreak > nul
start "" "http://localhost:5173"

echo ProdiPath siap dibuka.
echo Pastikan Anda sudah menyalakan MySQL di XAMPP!
pause
