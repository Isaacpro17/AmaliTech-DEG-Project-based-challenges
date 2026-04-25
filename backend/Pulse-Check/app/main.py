from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.scheduler import start_scheduler
from app.routes import monitors

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle startup and shutdown logic.
    Starts the background watchdog scheduler on app startup.
    """
    start_scheduler()
    yield
    # Shutdown logic would go here if needed

app = FastAPI(
    title="Pulse-Check-API (Watchdog Sentinel)",
    version="1.0.0",
    description="A Dead Man's Switch API for monitoring remote devices.",
    lifespan=lifespan
)

# Include the routes from the monitors module
app.include_router(monitors.router, prefix="/monitors", tags=["Monitors"])

@app.get("/")
async def root():
    """
    Root endpoint to verify the service is healthy.
    """
    return {"message": "Watchdog Sentinel is running.", "status": "ok"}