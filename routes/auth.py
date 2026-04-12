from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import psycopg2.extras
from database import get_db_connection
import auth
import models

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

@router.post("/token", response_model=models.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection generic error")
    
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (form_data.username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user or not auth.verify_password(form_data.password, user['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user['email'], "rol": user['rol']}, expires_delta=access_token_expires
    )
    
    user_response = models.UsuarioResponse(
        id=user['id'],
        nombre=user['nombre'],
        apellido=user['apellido'],
        email=user['email'],
        rol=user['rol']
    )
    
    return {"access_token": access_token, "token_type": "bearer", "user": user_response}

# Reusable dependency to get current user info
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = models.TokenData(username=username)
    except auth.JWTError:
        raise credentials_exception
    
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection generic error")
        
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (token_data.username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user is None:
        raise credentials_exception
    
    return models.UsuarioResponse(
        id=user['id'],
        nombre=user['nombre'],
        apellido=user['apellido'],
        email=user['email'],
        rol=user['rol']
    )
