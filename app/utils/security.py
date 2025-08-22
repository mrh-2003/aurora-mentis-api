# app/utils/security.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from firebase_admin import auth
from app.firebase.firebase_admin import db as firestore_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_admin_user(token: str = Depends(oauth2_scheme)):
    """
    Decodifica el token de Firebase ID y verifica si el usuario tiene el rol de 'admin'.
    """
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token.get("uid")
        
        # Consultar el rol desde Firestore
        user_doc = firestore_db.collection('users').document(uid).get()
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario no tiene un rol definido."
            )
        user_role = user_doc.to_dict().get('role')
        
        if user_role not in ['admin', 'caja']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos insuficientes."
            )
            
        return decoded_token
        
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de autenticación: {e}"
        )