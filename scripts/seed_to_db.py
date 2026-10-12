import pandas as pd
import mysql.connector
import os
import sys

def seed_database():
    print("Starting database seed...")
    
    # Check if file exists
    csv_path = os.path.join(os.path.dirname(__file__), '../data/questionnaire_real.csv')
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        sys.exit(1)
        
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)
        
    print(f"Loaded {len(df)} records from CSV.")
    
    # Connect to database
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='metopen_db',
            user='root',
            password=''
        )
        cursor = conn.cursor()
    except Exception as e:
        print(f"Database connection failed: {e}")
        sys.exit(1)
        
    success_count = 0
    error_count = 0
    
    # Clear existing dummy data
    try:
        print("Clearing existing data...")
        cursor.execute("TRUNCATE TABLE questionnaire_data")
        conn.commit()
    except Exception as e:
        print(f"Failed to clear existing data: {e}")
        
    for index, row in df.iterrows():
        try:
            query = """
                INSERT INTO questionnaire_data 
                (npm, nama, program_studi, semester, konsistensi_belajar, manajemen_waktu, penyelesaian_tugas, 
                pemahaman_materi, konsentrasi_belajar, persiapan_ujian, keaktifan_pembelajaran, motivasi_belajar, 
                pemanfaatan_waktu_belajar, performa_belajar) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                nama=VALUES(nama), program_studi=VALUES(program_studi), semester=VALUES(semester),
                konsistensi_belajar=VALUES(konsistensi_belajar), manajemen_waktu=VALUES(manajemen_waktu),
                penyelesaian_tugas=VALUES(penyelesaian_tugas), pemahaman_materi=VALUES(pemahaman_materi),
                konsentrasi_belajar=VALUES(konsentrasi_belajar), persiapan_ujian=VALUES(persiapan_ujian),
                keaktifan_pembelajaran=VALUES(keaktifan_pembelajaran), motivasi_belajar=VALUES(motivasi_belajar),
                pemanfaatan_waktu_belajar=VALUES(pemanfaatan_waktu_belajar), performa_belajar=VALUES(performa_belajar)
            """
            values = (
                str(row['npm']), str(row['nama']), str(row['program_studi']), int(row['semester']),
                int(row['konsistensi_belajar']), int(row['manajemen_waktu']), int(row['penyelesaian_tugas']),
                int(row['pemahaman_materi']), int(row['konsentrasi_belajar']), int(row['persiapan_ujian']),
                int(row['keaktifan_pembelajaran']), int(row['motivasi_belajar']), int(row['pemanfaatan_waktu_belajar']),
                str(row['performa_belajar'])
            )
            cursor.execute(query, values)
            success_count += 1
        except Exception as e:
            error_count += 1
            print(f"Error row {index}: {e}")
            
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"Seeding completed. Success: {success_count}, Errors: {error_count}")

if __name__ == "__main__":
    seed_database()
