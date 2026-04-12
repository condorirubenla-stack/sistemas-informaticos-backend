from fastapi import APIRouter, Depends, HTTPException
from typing import List
import psycopg2.extras
from database import get_db_connection
from routes.auth import get_current_user
import models

router = APIRouter()

@router.get("/", response_description="Lista de módulos")
def get_modulos():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM modulos ORDER BY nivel, subnivel")
    modulos = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return {"modulos": modulos}

@router.post("/", dependencies=[Depends(get_current_user)])
def create_modulo(nombre: str, nivel: str, subnivel: str = None):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    
    cursor = conn.cursor()
    cursor.execute("INSERT INTO modulos (nombre, nivel, subnivel) VALUES (%s, %s, %s) RETURNING id", (nombre, nivel, subnivel))
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    
    return {"id": new_id, "mensaje": "Módulo creado exitosamente"}

@router.get("/{modulo_id}/contenidos")
def get_contenidos(modulo_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
        
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM contenidos WHERE modulo_id = %s", (modulo_id,))
    contenidos = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return {"contenidos": contenidos}

@router.put("/contenidos/{contenido_id}")
def update_contenido(contenido_id: int, url: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    
    cursor = conn.cursor()
    cursor.execute("UPDATE contenidos SET url = %s WHERE id = %s", (url, contenido_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    return {"mensaje": "Contenido actualizado correctamente"}
