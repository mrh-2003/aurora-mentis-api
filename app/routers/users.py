# app/routers/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from firebase_admin import auth
from app.utils.security import get_current_admin_user
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
async def update_user_status(uid: str, payload: UserStatusUpdate):
    """
    Activa o desactiva un usuario en Firebase Authentication.
    """
    try:
        auth.update_user(uid, disabled=payload.is_disabled)
        status_text = "desactivado" if payload.is_disabled else "activado"
        logger.info(f"Admin cambió el estado del usuario {uid} a {status_text}.")
        return {"message": f"Usuario {status_text} correctamente."}
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