# Final stable version for EduConnect Ruben
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
    db_status = "error"
    db_detail = "No se detectó DATABASE_URL ni INTERNAL_DATABASE_URL"
    
    try:
        from database import get_db_connection
        conn = get_db_connection()
        if conn:
            db_status = "connected"
            db_detail = "Conexión exitosa"
            conn.close()
    except Exception as e:
        db_detail = str(e)

    return {
        "client": "EduConnect Ruben",
        "status": "online",
        "version": "2.2.2 PRO",
        "database": db_status == "connected",
        "hash_check": db_detail if db_status != "connected" else "Check /cargar-datos",
        "author": "Antigravity AI"

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


