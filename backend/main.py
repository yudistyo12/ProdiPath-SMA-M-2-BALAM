from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import auth, students, dataset, predict, dashboard, analysis

app = FastAPI(
    title="ProdiPath API",
    description="API prototipe rekomendasi jurusan kuliah untuk siswa kelas XII.",
)

# Setup CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(dataset.router)
app.include_router(predict.router)
app.include_router(dashboard.router)
app.include_router(analysis.router)

@app.get("/")
def read_root():
    return {"message": "ProdiPath API aktif"}
