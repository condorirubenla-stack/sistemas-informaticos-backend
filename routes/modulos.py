from fastapi import APIRouter, Depends, HTTPException
from database import get_db_connection
from routes.auth import get_current_user

router = APIRouter()

def rows_to_dicts(cursor, rows):
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, r)) for r in rows]

# ── LIST ALL MODULES ─────────────────────────────────────────────────────────
@router.get("/")
def get_modulos():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, nivel, subnivel, orden FROM modulos ORDER BY nivel, orden, id")
        modulos = rows_to_dicts(cur, cur.fetchall())
        return {"modulos": modulos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ── LIST MODULES BY NIVEL ────────────────────────────────────────────────────
@router.get("/nivel/{nivel}")
def get_modulos_by_nivel(nivel: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, nivel, subnivel, orden FROM modulos WHERE nivel = %s ORDER BY orden, id", (nivel,))
        modulos = rows_to_dicts(cur, cur.fetchall())
        return {"modulos": modulos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ── CREATE MODULE ─────────────────────────────────────────────────────────────
@router.post("/", dependencies=[Depends(get_current_user)])
def create_modulo(nombre: str, nivel: str, subnivel: str = ""):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    try:
        cur = conn.cursor()
        cur.execute("SELECT COALESCE(MAX(orden),0)+1 FROM modulos WHERE nivel=%s", (nivel,))
        next_order = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO modulos (nombre, nivel, subnivel, orden) VALUES (%s,%s,%s,%s) RETURNING id",
            (nombre, nivel, subnivel, next_order)
        )
        mod_id = cur.fetchone()[0]
        # Create 4 topics × 5 material types
        for tema_num in range(1, 5):
            for tipo in ["teoria","video","audio","presentacion","evaluacion"]:
                cur.execute(
                    "INSERT INTO contenidos (modulo_id, tipo, titulo, url, tema_num) VALUES (%s,%s,%s,%s,%s)",
                    (mod_id, tipo, f"Tema {tema_num} - {tipo.capitalize()}", "", tema_num)
                )
        conn.commit()
        return {"id": mod_id, "mensaje": "Módulo creado con 4 temas"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ── UPDATE MODULE (rename / reorder) ─────────────────────────────────────────
@router.put("/{modulo_id}", dependencies=[Depends(get_current_user)])
def update_modulo(modulo_id: int, nombre: str = None, orden: int = None):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    try:
        cur = conn.cursor()
        if nombre:
            cur.execute("UPDATE modulos SET nombre=%s WHERE id=%s", (nombre, modulo_id))
        if orden is not None:
            cur.execute("UPDATE modulos SET orden=%s WHERE id=%s", (orden, modulo_id))
        conn.commit()
        return {"mensaje": "Módulo actualizado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ── DELETE MODULE ─────────────────────────────────────────────────────────────
@router.delete("/{modulo_id}", dependencies=[Depends(get_current_user)])
def delete_modulo(modulo_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM modulos WHERE id=%s", (modulo_id,))
        conn.commit()
        return {"mensaje": "Módulo eliminado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ── GET CONTENTS (by module, grouped by topic) ────────────────────────────────
@router.get("/{modulo_id}/contenidos")
def get_contenidos(modulo_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    try:
        cur = conn.cursor()
        
        # Self-healing: Asegurar que existan los 4 temas × 5 materiales
        tipos = ["teoria", "video", "audio", "presentacion", "evaluacion"]
        for tema_num in range(1, 5):
            for tipo in tipos:
                cur.execute(
                    "SELECT id FROM contenidos WHERE modulo_id = %s AND tema_num = %s AND tipo = %s",
                    (modulo_id, tema_num, tipo)
                )
                if not cur.fetchone():
                    cur.execute(
                        "INSERT INTO contenidos (modulo_id, tipo, titulo, url, tema_num) VALUES (%s, %s, %s, %s, %s)",
                        (modulo_id, tipo, f"Tema {tema_num} - {tipo.capitalize()}", "", tema_num)
                    )
        conn.commit()

        # Retornar todos los contenidos
        cur.execute("SELECT id, modulo_id, tipo, titulo, url, tema_num FROM contenidos WHERE modulo_id=%s ORDER BY tema_num, tipo", (modulo_id,))
        contenidos = rows_to_dicts(cur, cur.fetchall())
        return {"contenidos": contenidos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# ── POST NEW CONTENT (dynamic addition) ───────────────────────────────────────
@router.post("/{modulo_id}/contenidos", dependencies=[Depends(get_current_user)])
def add_contenido_extra(modulo_id: int, tipo: str, titulo: str, url: str, tema_num: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO contenidos (modulo_id, tipo, titulo, url, tema_num) VALUES (%s,%s,%s,%s,%s) RETURNING id",
            (modulo_id, tipo, titulo, url, tema_num)
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        return {"mensaje": "Material agregado", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ── UPDATE CONTENT URL ────────────────────────────────────────────────────────
@router.put("/contenidos/{contenido_id}")
def update_contenido(contenido_id: int, url: str, titulo: str = None):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    try:
        cur = conn.cursor()
        if titulo:
            cur.execute("UPDATE contenidos SET url=%s, titulo=%s WHERE id=%s", (url, titulo, contenido_id))
        else:
            cur.execute("UPDATE contenidos SET url=%s WHERE id=%s", (url, contenido_id))
        conn.commit()
        return {"mensaje": "Contenido actualizado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ── ADMIN: students per nivel with grades ─────────────────────────────────────
@router.get("/admin/inscritos")
def get_inscritos_por_nivel():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT u.id, u.nombre, u.apellido, u.email, m.nivel, m.nombre AS modulo, p.estado, p.nota, p.id AS progreso_id
            FROM progreso p
            JOIN usuarios u ON u.id = p.usuario_id
            JOIN modulos m ON m.id = p.modulo_id
            ORDER BY m.nivel, u.apellido
        """)
        inscritos = rows_to_dicts(cur, cur.fetchall())
        return {"inscritos": inscritos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ── ADMIN: Asignar nota a un estudiante en un módulo ──────────────────────────
@router.put("/admin/inscritos/{progreso_id}/nota", dependencies=[Depends(get_current_user)])
def asignar_nota(progreso_id: int, nota: float):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    try:
        cur = conn.cursor()
        estado = 'aprobado' if nota >= 61 else 'reprobado'
        cur.execute("UPDATE progreso SET nota=%s, estado=%s WHERE id=%s", (nota, estado, progreso_id))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Registro de progreso no encontrado")
        conn.commit()
        return {"mensaje": "Nota asignada correctamente", "estado": estado, "nota": nota}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ── STUDENT: get own grades ───────────────────────────────────────────────────
@router.get("/mis-notas", dependencies=[Depends(get_current_user)])
def get_mis_notas(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    try:
        cur = conn.cursor()
        cur.execute("SELECT modulo_id, estado, nota FROM progreso WHERE usuario_id=%s", (current_user["id"],))
        return {"progreso": rows_to_dicts(cur, cur.fetchall())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
