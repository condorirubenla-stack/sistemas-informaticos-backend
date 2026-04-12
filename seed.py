import os
import psycopg2
from dotenv import load_dotenv
import security as auth

load_dotenv()

def seed_users():
    print("Iniciando creación de usuarios...")
    try:
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            connection = psycopg2.connect(db_url)
        else:
            # Fallback local usando postgres
            connection = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "root"),
                dbname=os.getenv("DB_NAME", "educonnect_ruben")
            )
        
        cursor = connection.cursor()

        # 1. Crear Administrador
        admin_pass = auth.get_password_hash("1234567")
        cursor.execute("""
            INSERT INTO usuarios (nombre, apellido, email, password, rol) 
            VALUES (%s, %s, %s, %s, %s) 
            ON CONFLICT (email) DO UPDATE SET password = EXCLUDED.password, rol = EXCLUDED.rol
        """, ("Ruben", "Admin", "ruben.admin@educonnect.com", admin_pass, "administrador"))

        # 2. Crear Estudiante
        estudiante_pass = auth.get_password_hash("9876543")
        cursor.execute("""
            INSERT INTO usuarios (nombre, apellido, email, password, rol) 
            VALUES (%s, %s, %s, %s, %s) 
            ON CONFLICT (email) DO UPDATE SET password = EXCLUDED.password
        """, ("Juan", "Perez", "juan.perez@educonnect.com", estudiante_pass, "estudiante"))

        connection.commit()
        print("¡Usuarios creados exitosamente en PostgreSQL!")
        
    except Exception as e:
        print(f"Error al insertar usuarios: {e}")
    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    seed_users()
