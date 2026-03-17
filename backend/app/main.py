"""
FastAPI Application Entry Point
AI Brand Identity Builder Platform
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from app.db.database import init_db
from app.api.brand import router as brand_router
from app.api.regenerate import router as regenerate_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create DB tables. Shutdown: cleanup."""
    await init_db()
    # Ensure export dirs exist
    os.makedirs("exports", exist_ok=True)
    os.makedirs("generated_logos", exist_ok=True)
    yield


app = FastAPI(
    title="AI Brand Identity Builder",
    description="Multi-agent pipeline that transforms a raw business idea into a complete brand identity.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        frontend_url,
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static file dirs for exports and logos
app.mount("/exports", StaticFiles(directory="exports"), name="exports")
app.mount("/logos", StaticFiles(directory="generated_logos"), name="logos")

# Register API routers
app.include_router(brand_router)
app.include_router(regenerate_router)


@app.get("/")
async def root():
    return {
        "message": "AI Brand Identity Builder API",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
