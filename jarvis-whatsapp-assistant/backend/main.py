from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import logging
from contextlib import asynccontextmanager

# Import our modules
from app.core.config import settings
from app.core.redis_client import redis_client
from app.api.webhooks import router as webhook_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting JARVIS WhatsApp Assistant...")
    await redis_client.connect()
    yield
    # Shutdown
    logger.info("Shutting down JARVIS WhatsApp Assistant...")
    await redis_client.disconnect()

# Create FastAPI app
app = FastAPI(
    title="JARVIS WhatsApp Assistant",
    description="AI-powered WhatsApp assistant for task automation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhook_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "JARVIS WhatsApp Assistant API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Redis connection
        redis_status = await redis_client.exists("health_check")
        return {
            "status": "healthy",
            "redis": "connected" if redis_client.redis_client else "disconnected",
            "openai_configured": bool(settings.OPENAI_API_KEY),
            "whatsapp_configured": bool(settings.WHATSAPP_ACCESS_TOKEN)
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
