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
    init_db()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, restrict to actual frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(modulos.router, prefix="/modulos", tags=["Modulos"])
app.include_router(evaluaciones.router, prefix="/evaluaciones", tags=["Evaluaciones"])

@app.get("/")
def read_root():
    return {"message": "Welcome to EduConnect-Ruben API"}

@app.get("/cargar-datos")
def instalar_datos_iniciales():
    try:
        from seed import seed_users
        from seed_modulos import seed_data
        seed_users()
        seed_data()
        
        # Verify
        from database import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT email, rol FROM usuarios")
        users = cur.fetchall()
        cur.close(); conn.close()
        
        return {
            "mensaje": "¡Éxito! Base de datos inicializada.",
            "usuarios_en_db": [u[0] for u in users],
            "admin_confirmado": "ruben.admin@educonnect.com" in [u[0] for u in users]
        }
    except Exception as e:
        return {"error": str(e)}
