"""
main.py
-------
FastAPI application entry point.

This file:
  1. Creates the FastAPI app instance.
  2. Adds CORS middleware (so the mobile app can talk to this API).
  3. Registers all routers (one per resource).
  4. Defines a health-check endpoint so you can verify the server is running.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import every router
from app.routers import estates, users, workers, tea_entries, attendance, reports
from app.config import settings

# ── App Instance ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="🍃 Tea Estate Management API",
    description="Backend for the Tea Estate Management mobile application.",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI — open in browser when running locally
    redoc_url="/redoc",
)

# ── CORS Middleware ───────────────────────────────────────────────────────────
# Allows the mobile app (and any future web dashboard) to make requests.
# In production, replace "*" with your actual domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # TODO: lock down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ──────────────────────────────────────────────────────────
# Every router gets a /api/v1 prefix so future versions won't break old clients.
API_PREFIX = "/api/v1"

app.include_router(estates.router,     prefix=API_PREFIX)
app.include_router(users.router,       prefix=API_PREFIX)
app.include_router(workers.router,     prefix=API_PREFIX)
app.include_router(tea_entries.router, prefix=API_PREFIX)
app.include_router(attendance.router,  prefix=API_PREFIX)
app.include_router(reports.router,     prefix=API_PREFIX)

# ── Health Check ─────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    """Quick check that the server is alive."""
    return {"status": "ok", "message": "Tea Estate API is running 🍃"}
