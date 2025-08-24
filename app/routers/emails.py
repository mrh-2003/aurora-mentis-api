# app/routers/emails.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from app.schemas.email import PaymentNotificationEmail, ScholarshipNotificationEmail,PlatformAssignmentEmail
from app.services.email_service import EmailService, email_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/emails",
    tags=["Emails"],
    responses={404: {"description": "Not found"}},
)

@router.post("/send-payment-notification", status_code=status.HTTP_202_ACCEPTED)
async def send_payment_notification_endpoint(details: PaymentNotificationEmail, background_tasks: BackgroundTasks, service: EmailService = Depends(lambda: email_service)):
    try:
        logger.info(f"Adding payment notification task for {details.student_email}")
        background_tasks.add_task(service.send_payment_notification, details)
        return {"message": "La notificación de pago ha sido programada para envío."}
    except Exception as e:
        logger.error(f"Error scheduling payment notification email: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo programar el envío del correo de notificación.")

@router.post("/send-scholarship-notification", status_code=status.HTTP_202_ACCEPTED)
async def send_scholarship_notification_endpoint(details: ScholarshipNotificationEmail, background_tasks: BackgroundTasks, service: EmailService = Depends(lambda: email_service)):
    """
    Endpoint para enviar una notificación de beca.
    """
    try:
        logger.info(f"Adding scholarship notification task for {details.student_email}")
        background_tasks.add_task(service.send_scholarship_notification, details)
        return {"message": "La notificación de beca ha sido programada para envío."}
    except Exception as e:
        logger.error(f"Error scheduling scholarship notification email: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo programar el envío del correo de notificación.")
    
@router.post("/send-platform-assignment", status_code=status.HTTP_202_ACCEPTED)
async def send_platform_assignment_endpoint(details: PlatformAssignmentEmail, background_tasks: BackgroundTasks, service: EmailService = Depends(lambda: email_service)):
    """
    Endpoint para enviar una notificación de asignación de plataformas.
    """
    try:
        logger.info(f"Adding platform assignment notification task for {details.student_email}")
        background_tasks.add_task(service.send_platform_assignment_notification, details)
        return {"message": "La notificación de asignación de plataformas ha sido programada."}
    except Exception as e:
        logger.error(f"Error scheduling platform assignment email: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo programar el envío del correo.")