from fastapi import APIRouter, Depends, HTTPException
import psycopg2.extras
from database import get_db_connection
from routes.auth import get_current_user
import models

router = APIRouter()

@router.get("/{modulo_id}")
def get_evaluacion(modulo_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM evaluaciones WHERE modulo_id = %s", (modulo_id,))
    evaluaciones = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"evaluaciones": evaluaciones}

@router.post("/submit", dependencies=[Depends(get_current_user)])
def submit_evaluacion(modulo_id: int, respuestas: dict, current_user: models.UsuarioResponse = Depends(get_current_user)):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de DB")
    
    # Very simplified evaluation mock logic:
    # Just insert progress for demonstration
    nota = 100.0 # Mock Note
    estado = "completado"
    
    cursor = conn.cursor()
    try:
        # Check if progress exists
        cursor.execute("SELECT * FROM progreso WHERE usuario_id=%s AND modulo_id=%s", (current_user.id, modulo_id))
        prog = cursor.fetchone()
        if prog:
            cursor.execute("UPDATE progreso SET estado=%s, nota=%s WHERE usuario_id=%s AND modulo_id=%s", 
                           (estado, nota, current_user.id, modulo_id))
        else:
            cursor.execute("INSERT INTO progreso (usuario_id, modulo_id, estado, nota) VALUES (%s, %s, %s, %s)",
                           (current_user.id, modulo_id, estado, nota))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
        
    return {"mensaje": "Evaluación guardada correctamente", "nota": nota}
