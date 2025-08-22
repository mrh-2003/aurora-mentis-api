# app/services/email_service.py

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.schemas.email import PaymentNotificationEmail, PaymentReminderEmail
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    """
    Servicio para construir y enviar correos electrónicos de manera asíncrona.
    """

    async def _send_email(self, recipients: List[str], subject: str, html_content: str):
        """
        Método base para enviar un correo electrónico usando SMTP.
        """
        if not recipients:
            logger.warning("No recipients provided for email.")
            return

        message = MIMEMultipart("alternative")
        message["From"] = f"ADE Academy <{settings.SMTP_USER}>"
        message["To"] = ", ".join(recipients)
        message["Subject"] = subject
        message.attach(MIMEText(html_content, "html"))

        try:
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=True,
            )
            logger.info(f"Email sent successfully to: {', '.join(recipients)}")
        except Exception as e:
            logger.error(f"Failed to send email to {', '.join(recipients)}: {e}")

    async def send_payment_notification(self, details: PaymentNotificationEmail):
        """
        Envía una notificación de pago exitoso.
        """
        subject = "Confirmación de Pago - ADE Academy"
        html_content = f"""
        <html>
            <body>
                <h2>¡Gracias por tu pago, {details.student_name}!</h2>
                <p>Hemos registrado correctamente tu pago en nuestro sistema.</p>
                <ul>
                    <li><strong>Monto Pagado:</strong> S/ {details.payment_amount:.2f}</li>
                    <li><strong>Fecha de Pago:</strong> {details.payment_date}</li>
                    <li><strong>Tu próxima fecha de pago es:</strong> {details.new_due_date}</li>
                </ul>
                <p>Gracias por ser parte de <strong>ADE Academy</strong>.</p>
            </body>
        </html>
        """
        recipients = [details.student_email]
        if details.guardian_email:
            recipients.append(details.guardian_email)
        
        await self._send_email(recipients, subject, html_content)

    async def send_payment_reminder(self, details: PaymentReminderEmail):
        """
        Envía un recordatorio de pago pendiente. 
        """
        subject = "Recordatorio de Pago Pendiente - ADE Academy"
        html_content = f"""
        <html>
            <body>
                <h2>Recordatorio de Pago, {details.student_name}</h2>
                <p>Te escribimos para recordarte que tienes un pago pendiente con la academia.</p>
                <ul>
                    <li><strong>Monto a Pagar:</strong> S/ {details.amount_due:.2f}</li>
                    <li><strong>Fecha de Vencimiento:</strong> {details.due_date}</li>
                </ul>
                <p>Por favor, realiza tu pago a la brevedad para evitar la desactivación de tu cuenta.</p>
                <p>Atentamente,<br>El equipo de <strong>ADE Academy</strong>.</p>
            </body>
        </html>
        """
        recipients = [details.student_email]
        if details.guardian_email:
            recipients.append(details.guardian_email)
            
        await self._send_email(recipients, subject, html_content)

# Instancia global del servicio
email_service = EmailService()