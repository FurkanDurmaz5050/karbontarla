from __future__ import annotations

"""KarbonTarla — FastAPI uygulama girişi."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import traceback
import logging

from app.config import get_settings
from app.database import init_db, ensure_seeded
from app.routers import auth, farmers, fields, sensors, satellite, carbon, reports, marketplace, seed

settings = get_settings()
logger = logging.getLogger("karbontarla")

_initialized = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _initialized
    try:
        await init_db()
        await ensure_seeded()
        pdf_dir = settings.PDF_OUTPUT_DIR
        if settings.ENVIRONMENT == "production":
            pdf_dir = "/tmp/reports"
        os.makedirs(pdf_dir, exist_ok=True)
        _initialized = True
    except Exception as e:
        logger.error(f"Lifespan init error: {e}")
    yield


app = FastAPI(
    title="KarbonTarla API",
    description="Türk çiftçilerini küresel karbon kredi pazarlarına bağlayan dijital platform",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def ensure_db_initialized(request: Request, call_next):
    """Vercel serverless lifespan desteği yoksa, ilk istekte DB'yi başlat."""
    global _initialized
    if not _initialized:
        await init_db()
        await ensure_seeded()
        pdf_dir = "/tmp/reports" if settings.ENVIRONMENT == "production" else settings.PDF_OUTPUT_DIR
        os.makedirs(pdf_dir, exist_ok=True)
        _initialized = True
    return await call_next(request)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    logger.error(f"Unhandled error: {exc}\n{tb}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": tb if settings.ENVIRONMENT != "production" else None},
    )

origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(farmers.router, prefix="/api/v1/farmers", tags=["Farmers"])
app.include_router(fields.router, prefix="/api/v1/fields", tags=["Fields"])
app.include_router(sensors.router, prefix="/api/v1/sensors", tags=["Sensors"])
app.include_router(satellite.router, prefix="/api/v1/satellite", tags=["Satellite"])
app.include_router(carbon.router, prefix="/api/v1/carbon", tags=["Carbon"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(marketplace.router, prefix="/api/v1/marketplace", tags=["Marketplace"])
app.include_router(seed.router, prefix="/api/v1/seed", tags=["Seed Data"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "KarbonTarla API"}
