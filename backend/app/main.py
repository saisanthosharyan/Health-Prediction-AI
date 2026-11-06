from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models import Patient
from app.routers.patients import router as patients_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables when the application starts.
    Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(
    title="Health Prediction API",
    description=(
        "Patient management application with CRUD operations "
        "and external AI-generated health observations."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients_router)


@app.get("/", tags=["Health Check"])
def root():
    return {
        "message": "Health Prediction API is running.",
        "status": "healthy",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health Check"])
def health_check():
    return {
        "status": "ok",
        "database": "configured",
    }