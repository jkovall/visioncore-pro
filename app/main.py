"""FastAPI application for VisionCore Pro"""
import os
from fastapi import FastAPI, Depends, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routers import upload, search, auth
from app.database import connect_to_mongo, close_mongo_connection

load_dotenv()

app = FastAPI(
    title="VisionCore Pro",
    description="Find similar products by uploading a photo with user authentication",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(search.router, prefix="/api", tags=["search"])

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB on startup"""
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown"""
    await close_mongo_connection()

@app.get("/")
async def root():
    """Serve the main upload page"""
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "static", "index.html"))

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "VisionCore Pro"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("VISIONCORE_PORT", 8501))
    host = os.getenv("VISIONCORE_HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
