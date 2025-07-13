# app/routers/emails.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from app.schemas.email import PaymentNotificationEmail
from app.services.email_service import EmailService, email_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/emails",
    tags=["Emails"],
    responses={404: {"description": "Not found"}},
)

@router.post("/send-payment-notification", status_code=status.HTTP_202_ACCEPTED)
async def send_payment_notification_endpoint(
    details: PaymentNotificationEmail,
    background_tasks: BackgroundTasks,
    service: EmailService = Depends(lambda: email_service)
):
    """
    Endpoint para enviar una notificación de pago.
    Se ejecuta como una tarea en segundo plano para no bloquear la respuesta al cliente.

    Args:
        details (PaymentNotificationEmail): Detalles del pago y del estudiante.
        background_tasks (BackgroundTasks): Gestor de tareas en segundo plano de FastAPI.
        service (EmailService): Instancia del servicio de correos.
    """
    try:
        logger.info(f"Adding payment notification task for {details.student_email}")
        background_tasks.add_task(service.send_payment_notification, details)
        return {"message": "La notificación de pago ha sido programada para envío."}
    except Exception as e:
        logger.error(f"Error scheduling payment notification email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo programar el envío del correo de notificación."
        )