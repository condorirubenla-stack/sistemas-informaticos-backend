from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from database import get_db_connection
import auth, psycopg2

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class TokenData(BaseModel):
    username: str | None = None

def rows_to_dicts(cursor, rows):
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, r)) for r in rows]

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, email, password, rol, nivel_asignado FROM usuarios WHERE email=%s", (form_data.username,))
    row = cur.fetchone()
    cur.close(); conn.close()
    if not row or not auth.verify_password(form_data.password, row[3]):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    token = auth.create_access_token(data={"sub": row[2]})
    return {"access_token": token, "token_type": "bearer",
            "rol": row[4], "nombre": row[1], "nivel_asignado": row[5]}

@router.get("/me")
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = auth.decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database error")
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, apellido, email, rol, nivel_asignado FROM usuarios WHERE email=%s", (payload.get("sub"),))
    row = cur.fetchone()
    cur.close(); conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"id": row[0], "nombre": row[1], "apellido": row[2], "email": row[3], "rol": row[4], "nivel_asignado": row[5]}

@router.post("/register-profesor", dependencies=[Depends(get_current_user)])
def register_profesor(nombre: str, apellido: str, email: str, password: str, nivel_asignado: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    try:
        cur = conn.cursor()
        hashed = auth.get_password_hash(password)
        cur.execute(
            "INSERT INTO usuarios (nombre, apellido, email, password, rol, nivel_asignado) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
            (nombre, apellido, email, hashed, "profesor", nivel_asignado)
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close(); conn.close()
        return {"id": new_id, "mensaje": f"Profesor {nombre} creado para nivel {nivel_asignado}"}
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/profesores")
def get_profesores():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, apellido, email, nivel_asignado FROM usuarios WHERE rol='profesor' ORDER BY nivel_asignado")
        return {"profesores": rows_to_dicts(cur, cur.fetchall())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
