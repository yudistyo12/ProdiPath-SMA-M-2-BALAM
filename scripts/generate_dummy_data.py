import pandas as pd
import numpy as np
import os
import random

def generate_data(num_samples=50):
    np.random.seed(42)
    random.seed(42)

    prodi_list = ['Informatika', 'Sistem Informasi', 'Teknologi Informasi', 'Teknik Komputer', 'Manajemen']
    
    data = []
    for i in range(num_samples):
        # Generate random NPM (e.g. 21312xxx)
        npm = f"21312{str(random.randint(0, 999)).zfill(3)}"
        nama = f"Mahasiswa {i+1}"
        prodi = random.choice(prodi_list)
        semester = random.choice([2, 4, 6, 8])
        
        # Base traits for correlation
        is_diligent = random.random() > 0.4
        
        if is_diligent:
            konsistensi = np.random.randint(3, 6)
            waktu = np.random.randint(3, 6)
            tugas = np.random.randint(4, 6)
            paham = np.random.randint(3, 6)
            konsentrasi = np.random.randint(3, 6)
            ujian = np.random.randint(3, 6)
            aktif = np.random.randint(2, 6)
            motivasi = np.random.randint(3, 6)
            manfaat = np.random.randint(3, 6)
            
            performa_score = (konsistensi + waktu + tugas + paham + konsentrasi + ujian + aktif + motivasi + manfaat) / 9
            if performa_score >= 4.2:
                performa = 'Tinggi'
            elif performa_score >= 3.5:
                performa = 'Sedang'
            else:
                performa = 'Sedang' # bias ke Sedang kalau rajin tapi skor nanggung
        else:
            konsistensi = np.random.randint(1, 4)
            waktu = np.random.randint(1, 4)
            tugas = np.random.randint(1, 4)
            paham = np.random.randint(1, 4)
            konsentrasi = np.random.randint(1, 4)
            ujian = np.random.randint(1, 4)
            aktif = np.random.randint(1, 4)
            motivasi = np.random.randint(1, 4)
            manfaat = np.random.randint(1, 4)
            
            performa_score = (konsistensi + waktu + tugas + paham + konsentrasi + ujian + aktif + motivasi + manfaat) / 9
            if performa_score < 2.5:
                performa = 'Rendah'
            else:
                performa = 'Sedang'
        
        data.append([
            npm, nama, prodi, semester, 
            konsistensi, waktu, tugas, paham, konsentrasi, 
            ujian, aktif, motivasi, manfaat, performa
        ])
    
    columns = [
        'npm', 'nama', 'program_studi', 'semester',
        'konsistensi_belajar', 'manajemen_waktu', 'penyelesaian_tugas', 'pemahaman_materi',
        'konsentrasi_belajar', 'persiapan_ujian', 'keaktifan_pembelajaran', 'motivasi_belajar',
        'pemanfaatan_waktu_belajar', 'performa_belajar'
    ]
    
    df = pd.DataFrame(data, columns=columns)
    # Ensure no exact duplicates of NPM
    df = df.drop_duplicates(subset=['npm'])
    
    return df

if __name__ == '__main__':
    df = generate_data(100) # generate 100 samples
    
    # Ensure data directory exists
    os.makedirs(os.path.join(os.path.dirname(__file__), '../data'), exist_ok=True)
    
    output_path = os.path.join(os.path.dirname(__file__), '../data/questionnaire_dummy.csv')
    df.to_csv(output_path, index=False)
    print(f"Dummy data generated successfully at {output_path} with {len(df)} records.")
