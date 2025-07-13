# app/schemas/user.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class Guardian(BaseModel):
    """
    Representa los datos del apoderado de un alumno.
    """
    name: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

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
    registration_date: str
    start_date: str
    monthly_fee: float
    assigned_platforms: List[str] = []
    status: str  # 'active' or 'inactive'
    has_scholarship: Optional[bool] = Field(default=False)
    guardian: Optional[Guardian] = None