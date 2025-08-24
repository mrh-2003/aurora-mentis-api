# app/routers/users.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from firebase_admin import auth
from app.utils.security import get_current_admin_user
from app.firebase.firebase_admin import db
from app.services.email_service import email_service
from app.schemas.email import AccountStatusNotificationEmail
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_admin_user)] # Protege todos los endpoints de este router
)

class UserStatusUpdate(BaseModel):
    is_disabled: bool

@router.patch("/{uid}/status", status_code=status.HTTP_200_OK)
async def update_user_status(uid: str, payload: UserStatusUpdate, background_tasks: BackgroundTasks):
    """
    Activa o desactiva un usuario en Firebase Authentication y envía una notificación.
    """
    try:
        # 1. Actualizar en Firebase Auth
        auth_user = auth.update_user(uid, disabled=payload.is_disabled)
        status_text = "desactivado" if payload.is_disabled else "activado"
        
        # 2. Obtener datos del alumno de Firestore para el correo
        students_ref = db.collection('students')
        query = students_ref.where('authUid', '==', uid).limit(1)
        student_docs = list(query.stream())

        if not student_docs:
            logger.warning(f"No se encontró un perfil de estudiante en Firestore para el UID {uid}. No se puede enviar correo.")
            return {"message": f"Usuario {status_text} correctamente, pero no se encontró perfil para notificar."}

        student_data = student_docs[0].to_dict()
        
        # 3. Enviar correo en segundo plano
        guardian_info = student_data.get('guardian')
        email_details = AccountStatusNotificationEmail(
            student_name=f"{student_data['first_name']} {student_data['last_name']}",
            student_email=auth_user.email,
            guardian_name=guardian_info.get('name') if guardian_info else None,
            guardian_email=guardian_info.get('email') if guardian_info else None,
            status="activada" if not payload.is_disabled else "desactivada"
        )
        background_tasks.add_task(email_service.send_account_status_notification, email_details)
        
        logger.info(f"Admin cambió el estado del usuario {uid} a {status_text} y se programó la notificación.")
        return {"message": f"Usuario {status_text} y notificado correctamente."}
        
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado en Firebase Authentication.")
    except Exception as e:
        logger.error(f"Error al cambiar el estado del usuario {uid}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{uid}", status_code=status.HTTP_200_OK)
async def delete_user_auth(uid: str):
    """
    Elimina un usuario de Firebase Authentication de forma permanente.
    """
    try:
        auth.delete_user(uid)
        logger.info(f"Admin eliminó permanentemente al usuario {uid} de Authentication.")
        return {"message": "Usuario eliminado de Authentication correctamente."}
    except auth.UserNotFoundError:
        # Si no se encuentra, no es un error crítico, puede que ya se haya borrado.
        logger.warning(f"Se intentó eliminar el usuario {uid} de Auth, pero no fue encontrado.")
        return {"message": "Usuario no encontrado en Authentication, pero la operación continúa."}
    except Exception as e:
        logger.error(f"Error al eliminar el usuario {uid} de Auth: {e}")
        raise HTTPException(status_code=500, detail=str(e))