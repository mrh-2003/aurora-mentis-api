# app/services/email_service.py

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.schemas.email import (
    PaymentNotificationEmail, 
    PaymentReminderEmail, 
    ScholarshipNotificationEmail,
    AccountDeactivationEmail,
    AccountStatusNotificationEmail,
    PlatformAssignmentEmail
)
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    """
    Servicio para construir y enviar correos electrónicos de manera asíncrona.
    """

    async def _send_email(self, recipients: List[str], subject: str, html_content: str):
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
        subject = "Confirmación de Pago - ADE Academy"
        debt_message = (f"<p><strong>Importante:</strong> Tienes un saldo pendiente de <strong>S/ {details.amount_due:.2f}</strong>. "
                        f"Tienes hasta el <strong>{details.payment_deadline}</strong> para completarlo.</p>") if details.amount_due > 0 else "<p>¡Excelente! No tienes deudas pendientes.</p>"
        html_content = f"""
        <html><body><h2>¡Gracias por tu pago, {details.student_name}!</h2><p>Hemos registrado correctamente tu pago en nuestro sistema.</p>
        <ul><li><strong>Monto Pagado:</strong> S/ {details.payment_amount:.2f}</li><li><strong>Fecha de Pago:</strong> {details.payment_date}</li></ul>
        {debt_message}<p>Gracias por ser parte de <strong>ADE Academy</strong>.</p></body></html>"""
        recipients = [details.student_email]
        if details.guardian_email: recipients.append(details.guardian_email)
        await self._send_email(recipients, subject, html_content)

    async def send_payment_reminder(self, details: PaymentReminderEmail):
        subject = "Recordatorio de Pago Pendiente - ADE Academy"
        html_content = f"""
        <html><body><h2>Recordatorio de Pago, {details.student_name}</h2><p>Te escribimos para recordarte que tienes un pago pendiente con la academia.</p>
        <ul><li><strong>Monto a Pagar:</strong> S/ {details.amount_due:.2f}</li><li><strong>Fecha de Vencimiento:</strong> {details.due_date}</li></ul>
        <p>Por favor, realiza tu pago a la brevedad para evitar la desactivación de tu cuenta.</p>
        <p>Atentamente,<br>El equipo de <strong>ADE Academy</strong>.</p></body></html>"""
        recipients = [details.student_email]
        if details.guardian_email: recipients.append(details.guardian_email)
        await self._send_email(recipients, subject, html_content)

    async def send_scholarship_notification(self, details: ScholarshipNotificationEmail):
        """
        Envía una notificación de beca aplicada.
        """
        subject = "¡Felicidades! Has recibido una Beca en ADE Academy"
        html_content = f"""
        <html>
            <body>
                <h2>¡Hola, {details.student_name}!</h2>
                <p>Nos complace informarte que se te ha otorgado una beca en la ADE Academy.</p>
                <ul>
                    <li><strong>Porcentaje de Beca:</strong> {details.percentage}%</li>
                    <li><strong>Tu nueva mensualidad es de:</strong> S/ {details.new_monthly_fee:.2f}</li>
                    <li><strong>Tu próxima fecha de pago es:</strong> {details.next_payment_date}</li>
                </ul>
                <p>¡Sigue esforzándote!</p>
                <p>Atentamente,<br>El equipo de <strong>ADE Academy</strong>.</p>
            </body>
        </html>
        """
        recipients = [details.student_email]
        if details.guardian_email:
            recipients.append(details.guardian_email)
        await self._send_email(recipients, subject, html_content)

    async def send_account_deactivation_notification(self, details: AccountDeactivationEmail):
        """
        Envía una notificación de cuenta inhabilitada por falta de pago.
        """
        subject = "Notificación: Acceso a la plataforma deshabilitado - ADE Academy"
        html_content = f"""
        <html>
            <body>
                <h2>Hola, {details.student_name}</h2>
                <p>Te informamos que el acceso a tu cuenta ha sido deshabilitado debido a un pago pendiente.</p>
                <ul>
                    <li><strong>Monto pendiente:</strong> S/ {details.amount_due:.2f}</li>
                </ul>
                <p>
                    Para reactivar tu acceso, por favor realiza el pago correspondiente y comunícate con nosotros al 
                    <strong>957-018-079</strong> para confirmar la operación.
                </p>
                <p>Agradecemos tu comprensión.</p>
                <p>Atentamente,<br>El equipo de <strong>ADE Academy</strong>.</p>
            </body>
        </html>
        """
        recipients = [details.student_email]
        if details.guardian_email:
            recipients.append(details.guardian_email)
        
        await self._send_email(recipients, subject, html_content)
    
    async def send_account_status_notification(self, details: AccountStatusNotificationEmail):
        """
        Notifica un cambio en el estado de la cuenta (activada/desactivada).
        """
        status_text = "ha sido activada" if details.status == "activada" else "ha sido desactivada"
        subject = f"Tu cuenta de ADE Academy {status_text}"
        
        message_body = ""
        if details.status == "activada":
            message_body = "<p>Nos complace informarte que tu acceso a la plataforma ha sido restaurado. ¡Ya puedes ingresar!</p>"
        else:
            message_body = "<p>Te informamos que tu acceso a la plataforma ha sido desactivado por un administrador. Si crees que es un error, por favor comunícate con nosotros.</p>"

        html_content = f"""
        <html><body><h2>¡Hola, {details.student_name}!</h2>{message_body}
        <p>Atentamente,<br>El equipo de <strong>ADE Academy</strong>.</p></body></html>
        """
        recipients = [details.student_email]
        if details.guardian_email: recipients.append(details.guardian_email)
        await self._send_email(recipients, subject, html_content)
        
    async def send_platform_assignment_notification(self, details: PlatformAssignmentEmail):
        """
        Envía una notificación con la lista de plataformas asignadas.
        """
        subject = "Bienvenido a ADE Academy - Tus Plataformas de Estudio"
        
        platforms_html = "<ul>"
        for platform in details.platforms:
            platforms_html += f"<li><strong>{platform['name']}:</strong> <a href='{platform['url']}'>Acceder aquí</a></li>"
        platforms_html += "</ul>"

        html_content = f"""
        <html><body><h2>¡Bienvenido, {details.student_name}!</h2>
        <p>Gracias por matricularte con nosotros. Tienes acceso a las siguientes plataformas de estudio:</p>
        {platforms_html}
        <p>Usa tu correo como usuario y contraseña para acceder a las cuentas. No olvides cambiar tu contraseña en Flyfar.</p>
        <p>Atentamente,<br>El equipo de <strong>ADE Academy</strong>.</p></body></html>
        """
        recipients = [details.student_email]
        if details.guardian_email: recipients.append(details.guardian_email)
        await self._send_email(recipients, subject, html_content)

email_service = EmailService()