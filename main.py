import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes import auth, modulos, evaluaciones
from database import init_db

load_dotenv()

app = FastAPI(title="EduConnect Ruben API", description="LMS Backend for educational platform")

@app.on_event("startup")
def startup_event():
    """Inicialización segura de la base de datos y datos maestros."""
    try:
        print("Verificando integridad de la base de datos...")
        init_db()
        
        # Auto-seed si no hay administrador
        from database import get_db_connection
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM usuarios WHERE email='ruben.admin@educonnect.com'")
            if not cur.fetchone():
                print("Administrador no encontrado. Ejecutando seeding automático...")
                from seed import seed_users
                from seed_modulos import seed_data
                seed_users()
                seed_data()
            cur.close(); conn.close()
    except Exception as e:
        print(f"WARNING: No se pudo auto-inicializar la DB en el arranque: {e}")

# CORS Configuration

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permitir todos los orígenes para facilitar integraciones
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(modulos.router, prefix="/modulos", tags=["Modulos"])
app.include_router(evaluaciones.router, prefix="/evaluaciones", tags=["Evaluaciones"])

@app.get("/")
def read_root():
    return {
        "client": "EduConnect Ruben",
        "status": "online",
        "version": "2.0.1 Pro",
        "has_db_url": bool(os.getenv("DATABASE_URL")),
        "db_url_prefix": os.getenv("DATABASE_URL")[:15] if os.getenv("DATABASE_URL") else "N/A"
    }


@app.get("/cargar-datos")
def instalar_datos_iniciales():
    """Endpoint manual para forzar la recarga de datos maestros."""
    try:
        from seed import seed_users
        from seed_modulos import seed_data
        
        success_users = seed_users()
        seed_data()
        
        # Verificación final
        from database import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT email, rol FROM usuarios")
        users = cur.fetchall()
        cur.close(); conn.close()
        
        return {
            "status": "success" if success_users else "partial_success",
            "mensaje": "Base de datos inicializada correctamente.",
            "usuarios_registrados": len(users),
            "admin_presente": "ruben.admin@educonnect.com" in [u[0] for u in users]
        }
    except Exception as e:
        return {"status": "error", "detalle": str(e)}

@app.get("/debug-db")
def debug_database():
    import os, psycopg2
    try:
        db_url = os.getenv("DATABASE_URL")
        res = {
            "has_url": bool(db_url),
            "url_starts_with": db_url[:20] if db_url else None,
            "env_keys": list(os.environ.keys())
        }
        
        # Test raw connection
        conn = None
        try:
            if db_url:
                conn = psycopg2.connect(db_url)
                res["raw_conn"] = "success"
                # Check tables
                cur = conn.cursor()
                cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
                res["tables"] = [t[0] for t in cur.fetchall()]
                cur.close()
            else:
                res["raw_conn"] = "no url"
        except Exception as conn_e:
            res["raw_conn"] = f"failed: {str(conn_e)}"
        finally:
            if conn: conn.close()
            
        return res
    except Exception as e:
        return {"error": str(e)}
