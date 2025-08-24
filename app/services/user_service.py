# app/services/user_service.py

from google.cloud.firestore_v1.client import Client
from firebase_admin import auth
from app.firebase.firebase_admin import db as firestore_db, auth_service
from app.services.email_service import email_service
from app.schemas.email import AccountDeactivationEmail
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserService:
    """
    Contiene la lógica de negocio relacionada con la gestión de usuarios
    en Firebase Authentication y Firestore.
    """

    def __init__(self, db: Client, auth_client: auth):
        self.db = db
        self.auth = auth_client
        self.users_ref = self.db.collection('students')

    def is_scholarship_active(self, scholarship_data: dict) -> bool:
        """
        Verifica si una beca está activa para el mes y año actual.
        """
        if not scholarship_data:
            return False
        try:
            today = datetime.now().date()
            start_date = datetime.strptime(scholarship_data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(scholarship_data['end_date'], '%Y-%m-%d').date()
            
            # La beca está activa si la fecha de hoy está dentro del rango
            return start_date <= today <= end_date
        except (ValueError, KeyError):
            return False

    def get_active_students_with_due_payments(self) -> list:
        """
        Obtiene una lista de todos los estudiantes activos con deuda y fecha de pago vencida.
        No considera a los estudiantes con beca activa para el mes actual.
        """
        try:
            today = datetime.now().date()
            students_snapshot = self.users_ref.where('status', '==', 'active').stream()
            overdue_students = []

            for student in students_snapshot:
                student_data = student.to_dict()
                student_data['id'] = student.id
                
                # Omitir si el estudiante tiene una beca activa
                if self.is_scholarship_active(student_data.get('scholarship')):
                    continue

                next_payment_date_str = student_data.get('next_payment_date')
                if not next_payment_date_str:
                    continue

                next_payment_date = datetime.strptime(next_payment_date_str, '%Y-%m-%d').date()

                # El alumno es moroso si su fecha de pago venció Y tiene deuda
                if next_payment_date < today and float(student_data.get('debt', 0)) > 0:
                    student_data['monthly_fee'] = float(student_data.get('monthly_fee', 0))
                    overdue_students.append(student_data)
            
            logger.info(f"Found {len(overdue_students)} overdue students.")
            return overdue_students

        except Exception as e:
            logger.error(f"Error fetching overdue students: {e}")
            return [] 
        
    async def deactivate_firebase_user(self, student_data: dict) -> bool:
        """
        Desactiva un usuario en Firebase Auth, actualiza su estado en Firestore y envía un correo de notificación.
        """
        student_id = student_data['id']
        email = student_data['email']
        
        try:
            # 1. Desactivar en Firebase Auth
            user = self.auth.get_user_by_email(email)
            self.auth.update_user(user.uid, disabled=True)
            logger.info(f"User {email} (UID: {user.uid}) disabled in Firebase Auth.")

            # 2. Actualizar estado en Firestore
            self.users_ref.document(student_id).update({'status': 'inactive'})
            logger.info(f"Student document {student_id} status updated to 'inactive' in Firestore.")
            
            # 3. Enviar correo de notificación
            guardian_info = student_data.get('guardian')
            email_details = AccountDeactivationEmail(
                student_name=f"{student_data['first_name']} {student_data['last_name']}",
                student_email=student_data['email'],
                guardian_name=guardian_info.get('name') if guardian_info else None,
                guardian_email=guardian_info.get('email') if guardian_info else None,
                amount_due=float(student_data.get('debt', 0))
            )
            await email_service.send_account_deactivation_notification(email_details)
            
            return True
        except auth.UserNotFoundError:
            logger.warning(f"User with email {email} not found in Firebase Auth. Updating Firestore only.")
            self.users_ref.document(student_id).update({'status': 'inactive'})
            return True # Aún se considera exitoso porque el estado en DB se actualizó
        except Exception as e:
            logger.error(f"Failed to deactivate user {email}: {e}")
            return False

user_service = UserService(db=firestore_db, auth_client=auth_service)