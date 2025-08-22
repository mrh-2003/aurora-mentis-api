# app/services/user_service.py

from google.cloud.firestore_v1.client import Client
from firebase_admin import auth
from app.firebase.firebase_admin import db as firestore_db, auth_service
from datetime import datetime, timedelta
import logging

# Configure logging
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

    def get_active_students_with_due_payments(self) -> list:
        """
        Obtiene una lista de todos los estudiantes activos cuya fecha de pago ha vencido.
        No considera a los estudiantes con beca para el mes actual.

        Returns:
            list: Una lista de documentos de estudiantes morosos.
        """
        try:
            today = datetime.now().date()
            students_snapshot = self.users_ref.where('status', '==', 'active').stream()
            print(students_snapshot)
            overdue_students = []

            for student in students_snapshot:
                student_data = student.to_dict()
                student_data['id'] = student.id
                
                # Omitir si el estudiante tiene una beca activa para el mes actual
                if student_data.get('has_scholarship_for_current_month', False):
                    continue

                # La fecha de próximo pago se almacena en 'next_payment_date'
                next_payment_date_str = student_data.get('next_payment_date')
                if not next_payment_date_str:
                    continue

                next_payment_date = datetime.strptime(next_payment_date_str, '%Y-%m-%d').date()

                if next_payment_date < today:
                    overdue_students.append(student_data)
            
            logger.info(f"Found {len(overdue_students)} overdue students.")
            return overdue_students

        except Exception as e:
            logger.error(f"Error fetching overdue students: {e}")
            return []

    def deactivate_firebase_user(self, student_id: str, email: str) -> bool:
        """
        Desactiva un usuario en Firebase Authentication y actualiza su estado en Firestore.

        Args:
            student_id (str): El ID del documento del estudiante en Firestore.
            email (str): El correo electrónico del usuario a desactivar en Firebase Auth.

        Returns:
            bool: True si la operación fue exitosa, False en caso contrario.
        """
        try:
            # 1. Desactivar en Firebase Auth
            user = self.auth.get_user_by_email(email)
            self.auth.update_user(user.uid, disabled=True)
            logger.info(f"User {email} (UID: {user.uid}) disabled in Firebase Auth.")

            # 2. Actualizar estado en Firestore
            self.users_ref.document(student_id).update({'status': 'inactive'})
            logger.info(f"Student document {student_id} status updated to 'inactive' in Firestore.")
            
            return True
        except auth.UserNotFoundError:
            logger.warning(f"User with email {email} not found in Firebase Auth. Updating Firestore only.")
            # Si el usuario no existe en Auth, al menos lo marcamos como inactivo en la DB
            self.users_ref.document(student_id).update({'status': 'inactive'})
            return True
        except Exception as e:
            logger.error(f"Failed to deactivate user {email}: {e}")
            return False

# Instancia global del servicio para ser usada en los routers
user_service = UserService(db=firestore_db, auth_client=auth_service)