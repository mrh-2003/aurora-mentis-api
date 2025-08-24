# app/schemas/email.py

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict

class EmailBase(BaseModel):
    """
    Modelo base para el envío de un correo.
    """
    student_name: str
    student_email: EmailStr
    guardian_name: Optional[str] = None
    guardian_email: Optional[EmailStr] = None

    @field_validator('guardian_email', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

class PaymentNotificationEmail(EmailBase):
    payment_amount: float
    payment_date: str
    amount_due: float
    payment_deadline: str

class PaymentReminderEmail(EmailBase):
    due_date: str
    amount_due: float

class ScholarshipNotificationEmail(EmailBase):
    percentage: int
    new_monthly_fee: float
    next_payment_date: str

class AccountDeactivationEmail(EmailBase):
    amount_due: float

class AccountStatusNotificationEmail(EmailBase):
    """
    Modelo para notificar activación o desactivación manual de la cuenta.
    """
    status: str # 'activada' o 'desactivada'

class PlatformAssignmentEmail(EmailBase):
    """
    Modelo para notificar la asignación de nuevas plataformas.
    """
    platforms: List[Dict[str, str]] # Lista de diccionarios [{'name': '...', 'url': '...'}]