# app/schemas/user.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class Guardian(BaseModel):
    """
    Representa los datos del apoderado de un alumno.
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

class Scholarship(BaseModel):
    """
    Representa los detalles de una beca para un alumno.
    """
    percentage: int = Field(..., gt=0, le=100) # Porcentaje de descuento
    start_date: str # Fecha de inicio de la beca
    end_date: str # Fecha de fin de la beca

class Student(BaseModel):
    """
    Representa el modelo de datos completo de un alumno, tal como
    se espera que esté en Firestore.
    """
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    start_date: str
    monthly_fee: float
    debt: float = Field(default=0.0)
    assigned_platforms: List[str] = []
    status: str  # 'active' or 'inactive'
    next_payment_date: str
    scholarship: Optional[Scholarship] = None
    guardian: Optional[Guardian] = None