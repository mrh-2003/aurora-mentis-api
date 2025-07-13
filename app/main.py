# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
import requests
import logging

from app.routers import emails, cron
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Scheduler Setup ---
scheduler = AsyncIOScheduler(timezone="America/Lima")

def run_deactivation_job():
    """Función para llamar al endpoint de desactivación."""
    url = "http://localhost:8000/cron/deactivate-overdue-users"
    try:
        response = requests.post(url)
        logger.info(f"Deactivation job triggered. Status: {response.status_code}, Response: {response.json()}")
    except requests.RequestException as e:
        logger.error(f"Error triggering deactivation job: {e}")

def run_reminder_job():
    """Función para llamar al endpoint de recordatorios."""
    url = "http://localhost:8000/cron/send-payment-reminders"
    try:
        response = requests.post(url)
        logger.info(f"Reminder job triggered. Status: {response.status_code}, Response: {response.json()}")
    except requests.RequestException as e:
        logger.error(f"Error triggering reminder job: {e}")

# --- FastAPI Lifespan Events ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación.
    Inicia el planificador al arrancar y lo detiene al apagar.
    """
    logger.info("Starting up application...")
    # Añadir tareas programadas
    scheduler.add_job(
        run_deactivation_job,
        CronTrigger(day=3, hour=2, minute=0), # Cada día 3 del mes a las 2:00 AM
        id="deactivate_users_job",
        name="Deactivate Overdue Users",
        replace_existing=True
    )
    scheduler.add_job(
        run_reminder_job,
        CronTrigger(day=30, hour=10, minute=0), # Cada día 30 del mes a las 10:00 AM
        id="send_reminders_job",
        name="Send Payment Reminders",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started.")
    yield
    logger.info("Shutting down application...")
    scheduler.shutdown()
    logger.info("Scheduler shut down.")


# --- FastAPI App Initialization ---
app = FastAPI(
    title="Aurora Mentis API",
    description="Backend para gestionar correos y tareas programadas para la academia Aurora Mentis.",
    version="1.0.0",
    lifespan=lifespan
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"], # Permite el origen del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
app.include_router(emails.router)
app.include_router(cron.router)

@app.get("/", tags=["Root"])
def read_root():
    """
    Endpoint raíz para verificar que el backend está funcionando.
    """
    return {"message": "Welcome to Aurora Mentis API. The system is running."}