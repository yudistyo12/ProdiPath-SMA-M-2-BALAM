from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


# === Auth ===
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    model_config = ConfigDict(from_attributes=True)


# === Questionnaire ===
class QuestionnaireBase(BaseModel):
    konsistensi_belajar: int = Field(ge=1, le=5)
    manajemen_waktu: int = Field(ge=1, le=5)
    penyelesaian_tugas: int = Field(ge=1, le=5)
    pemahaman_materi: int = Field(ge=1, le=5)
    konsentrasi_belajar: int = Field(ge=1, le=5)
    persiapan_ujian: int = Field(ge=1, le=5)
    keaktifan_pembelajaran: int = Field(ge=1, le=5)
    motivasi_belajar: int = Field(ge=1, le=5)
    pemanfaatan_waktu_belajar: int = Field(ge=1, le=5)
    performa_belajar: str

class QuestionnaireOut(QuestionnaireBase):
    id: int
    student_id: int
    model_config = ConfigDict(from_attributes=True)


# === Prediction ===
class PredictionOut(BaseModel):
    id: int
    student_id: int
    predicted_performance: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# === Student ===
class StudentBase(BaseModel):
    npm: str
    program_studi: str
    semester: int

class StudentCreate(StudentBase):
    questionnaire: Optional[QuestionnaireBase] = None

class StudentUpdate(StudentBase):
    questionnaire: Optional[QuestionnaireBase] = None

class StudentOut(StudentBase):
    id: int
    questionnaire: Optional[QuestionnaireOut] = None
    predictions: List[PredictionOut] = []
    model_config = ConfigDict(from_attributes=True)


# === Prediction Input ===
class PredictionInput(BaseModel):
    konsistensi_belajar: int = Field(ge=1, le=5)
    manajemen_waktu: int = Field(ge=1, le=5)
    penyelesaian_tugas: int = Field(ge=1, le=5)
    pemahaman_materi: int = Field(ge=1, le=5)
    konsentrasi_belajar: int = Field(ge=1, le=5)
    persiapan_ujian: int = Field(ge=1, le=5)
    keaktifan_pembelajaran: int = Field(ge=1, le=5)
    motivasi_belajar: int = Field(ge=1, le=5)
    pemanfaatan_waktu_belajar: int = Field(ge=1, le=5)
    student_id: Optional[int] = None

class PredictionResult(BaseModel):
    predicted_performance: str
    student_id: Optional[int] = None
