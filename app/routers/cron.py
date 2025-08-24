# app/routers/cron.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from app.services.user_service import UserService, user_service
from app.services.email_service import EmailService, email_service
from app.schemas.email import PaymentReminderEmail
from app.schemas.user import Guardian
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/cron",
    tags=["Cron Jobs"],
    responses={404: {"description": "Not found"}},
)

@router.post("/send-payment-reminders", status_code=status.HTTP_200_OK)
async def trigger_payment_reminders(
    background_tasks: BackgroundTasks,
    user_srv: UserService = Depends(lambda: user_service),
    email_srv: EmailService = Depends(lambda: email_service)
):
    """
    Endpoint para la tarea programada que envía recordatorios de pago.
    Obtiene los estudiantes activos que no han pagado y les envía un correo.
    """
    logger.info("CRON JOB: Starting 'send_payment_reminders' task.")
    overdue_students = user_srv.get_active_students_with_due_payments()

    if not overdue_students:
        logger.info("CRON JOB: No overdue students found. Task finished.")
        return {"message": "No hay estudiantes con pagos vencidos."}

    for student in overdue_students:
        guardian_info = student.get('guardian')
        reminder_details = PaymentReminderEmail(
            student_name=f"{student['first_name']} {student['last_name']}",
            student_email=student['email'],
            due_date=student['next_payment_date'],
            amount_due=student['monthly_fee'],
            guardian_name=guardian_info.get('name') if guardian_info else None,
            guardian_email=guardian_info.get('email') if guardian_info else None,
        )
        background_tasks.add_task(email_srv.send_payment_reminder, reminder_details)

    logger.info(f"CRON JOB: Scheduled {len(overdue_students)} payment reminders.")
    return {"message": f"Se programó el envío de {len(overdue_students)} recordatorios de pago."}


@router.post("/deactivate-overdue-users", status_code=status.HTTP_200_OK)
async def trigger_deactivation_of_overdue_users(
    background_tasks: BackgroundTasks, # Añadimos BackgroundTasks
    user_srv: UserService = Depends(lambda: user_service)
):
    """
    Endpoint para la tarea programada que desactiva usuarios morosos y les notifica.
    """
    logger.info("CRON JOB: Starting 'deactivate_overdue_users' task.")
    overdue_students = user_srv.get_active_students_with_due_payments()

    if not overdue_students:
        logger.info("CRON JOB: No users to deactivate. Task finished.")
        return {"message": "No hay usuarios morosos para desactivar."}

    deactivated_count = 0
    for student in overdue_students:
        # Usamos background_tasks para que la desactivación y envío de correo no bloqueen el proceso
        background_tasks.add_task(user_srv.deactivate_firebase_user, student)
        deactivated_count += 1
        
    logger.info(f"CRON JOB: Scheduled deactivation for {deactivated_count} users.")
    return {"message": f"Se programó la desactivación y notificación para {deactivated_count} usuarios morosos."}