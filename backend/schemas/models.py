from typing import Literal

from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class QuestionnaireData(BaseModel):
    nisn: str = Field(..., min_length=10, max_length=10, pattern=r"^[0-9]{10}$")
    nama: str = Field(..., min_length=1, max_length=100)
    jurusan_sma: Literal["IPA", "IPS", "Bahasa"]
    nilai_matematika: int = Field(..., ge=0, le=100)
    nilai_sains: int = Field(..., ge=0, le=100)
    nilai_sosial: int = Field(..., ge=0, le=100)
    nilai_bahasa: int = Field(..., ge=0, le=100)
    minat_teknologi: int = Field(..., ge=1, le=5)
    minat_seni: int = Field(..., ge=1, le=5)
    minat_komunikasi: int = Field(..., ge=1, le=5)
    kemampuan_analitis: int = Field(..., ge=1, le=5)
    rekomendasi_jurusan: str
    sumber_data: Literal["dataset", "kuesioner_web"]
    persetujuan_data: bool

class PredictionRequest(BaseModel):
    nisn: str = Field(..., min_length=10, max_length=10, pattern=r"^[0-9]{10}$")
    nama: str = Field(..., min_length=1, max_length=100)
    jurusan_sma: Literal["IPA", "IPS", "Bahasa"]
    nilai_matematika: int = Field(..., ge=0, le=100)
    nilai_sains: int = Field(..., ge=0, le=100)
    nilai_sosial: int = Field(..., ge=0, le=100)
    nilai_bahasa: int = Field(..., ge=0, le=100)
    minat_teknologi: int = Field(..., ge=1, le=5)
    minat_seni: int = Field(..., ge=1, le=5)
    minat_komunikasi: int = Field(..., ge=1, le=5)
    kemampuan_analitis: int = Field(..., ge=1, le=5)
    persetujuan_data: Literal[True]
