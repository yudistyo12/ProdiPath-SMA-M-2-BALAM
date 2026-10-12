from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum('admin', 'mahasiswa'), default='mahasiswa', nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    npm = Column(String(20), unique=True, nullable=False)
    program_studi = Column(String(100), nullable=False)
    semester = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    questionnaire = relationship(
        "QuestionnaireData", back_populates="student",
        cascade="all, delete-orphan", uselist=False
    )
    predictions = relationship(
        "Prediction", back_populates="student",
        cascade="all, delete-orphan"
    )


class QuestionnaireData(Base):
    __tablename__ = "questionnaire_data"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    nilai_matematika = Column(Integer, nullable=False)
    nilai_sains = Column(Integer, nullable=False)
    nilai_sosial = Column(Integer, nullable=False)
    nilai_bahasa = Column(Integer, nullable=False)
    minat_teknologi = Column(Integer, nullable=False)
    minat_seni = Column(Integer, nullable=False)
    minat_komunikasi = Column(Integer, nullable=False)
    kemampuan_analitis = Column(Integer, nullable=False)
    rekomendasi_jurusan = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    student = relationship("Student", back_populates="questionnaire")


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    predicted_jurusan = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    student = relationship("Student", back_populates="predictions")
