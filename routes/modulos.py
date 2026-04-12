from fastapi import APIRouter, Depends, HTTPException
from database import get_db_connection
from routes.auth import get_current_user

router = APIRouter()

@router.get("/", response_description="Lista de módulos")
def get_modulos():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, nivel, subnivel FROM modulos ORDER BY id")
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        modulos = [dict(zip(cols, row)) for row in rows]
        cursor.close()
        conn.close()
        return {"modulos": modulos}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", dependencies=[Depends(get_current_user)])
def create_modulo(nombre: str, nivel: str, subnivel: str = None):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO modulos (nombre, nivel, subnivel) VALUES (%s, %s, %s) RETURNING id", (nombre, nivel, subnivel))
        new_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return {"id": new_id, "mensaje": "Módulo creado exitosamente"}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{modulo_id}/contenidos")
def get_contenidos(modulo_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, modulo_id, tipo, titulo, url FROM contenidos WHERE modulo_id = %s", (modulo_id,))
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        contenidos = [dict(zip(cols, row)) for row in rows]
        cursor.close()
        conn.close()
        return {"contenidos": contenidos}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/contenidos/{contenido_id}")
def update_contenido(contenido_id: int, url: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE contenidos SET url = %s WHERE id = %s", (url, contenido_id))
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "Contenido actualizado correctamente"}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
