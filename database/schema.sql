CREATE DATABASE IF NOT EXISTS metopen_db;
USE metopen_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'mahasiswa') NOT NULL DEFAULT 'mahasiswa'
);

CREATE TABLE IF NOT EXISTS questionnaire_data (
    nisn VARCHAR(20) PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    jurusan_sma ENUM('IPA', 'IPS', 'Bahasa') NOT NULL,
    nilai_matematika TINYINT UNSIGNED NOT NULL,
    nilai_sains TINYINT UNSIGNED NOT NULL,
    nilai_sosial TINYINT UNSIGNED NOT NULL,
    nilai_bahasa TINYINT UNSIGNED NOT NULL,
    minat_teknologi TINYINT UNSIGNED NOT NULL,
    minat_seni TINYINT UNSIGNED NOT NULL,
    minat_komunikasi TINYINT UNSIGNED NOT NULL,
    kemampuan_analitis TINYINT UNSIGNED NOT NULL,
    rekomendasi_jurusan VARCHAR(100) NOT NULL,
    sumber_data ENUM('dataset', 'kuesioner_web') NOT NULL DEFAULT 'dataset',
    persetujuan_data BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_rekomendasi_jurusan (rekomendasi_jurusan),
    INDEX idx_sumber_data (sumber_data),
    CONSTRAINT chk_nilai_matematika CHECK (nilai_matematika <= 100),
    CONSTRAINT chk_nilai_sains CHECK (nilai_sains <= 100),
    CONSTRAINT chk_nilai_sosial CHECK (nilai_sosial <= 100),
    CONSTRAINT chk_nilai_bahasa CHECK (nilai_bahasa <= 100),
    CONSTRAINT chk_minat_teknologi CHECK (minat_teknologi BETWEEN 1 AND 5),
    CONSTRAINT chk_minat_seni CHECK (minat_seni BETWEEN 1 AND 5),
    CONSTRAINT chk_minat_komunikasi CHECK (minat_komunikasi BETWEEN 1 AND 5),
    CONSTRAINT chk_kemampuan_analitis CHECK (kemampuan_analitis BETWEEN 1 AND 5),
    CONSTRAINT chk_persetujuan_data CHECK (persetujuan_data IN (0, 1))
);
