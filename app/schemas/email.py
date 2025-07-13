# app/schemas/email.py

from pydantic import BaseModel, EmailStr
from typing import Optional, List

class EmailBase(BaseModel):
    """
    Modelo base para el envío de un correo.
    Contiene la información esencial para cualquier tipo de notificación.
    """
    student_name: str
    student_email: EmailStr
    guardian_name: Optional[str] = None
    guardian_email: Optional[EmailStr] = None

class PaymentNotificationEmail(EmailBase):
    """
    Modelo para el correo de notificación de un pago registrado.
    """
    payment_amount: float
    payment_date: str
    new_due_date: str

class PaymentReminderEmail(EmailBase):
    """
    Modelo para el correo de recordatorio de pago.
    """
    due_date: str
    amount_due: float