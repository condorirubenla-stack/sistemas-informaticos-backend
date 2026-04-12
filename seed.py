import os
import psycopg2
from dotenv import load_dotenv
import security as auth

load_dotenv()

from database import get_db_connection

def seed_users():
    """Crea el administrador y usuarios de prueba si no existen."""
    print("Iniciando creación de usuarios...")
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            print("Error: No se pudo obtener conexión para seeding.")
            return False
            
        cursor = connection.cursor()

        # 1. Crear Administrador - ruben.admin@educonnect.com / 1234567
        admin_pass = auth.get_password_hash("1234567")
        cursor.execute("""
            INSERT INTO usuarios (nombre, apellido, email, password, rol) 
            VALUES (%s, %s, %s, %s, %s) 
            ON CONFLICT (email) DO UPDATE SET password = EXCLUDED.password, rol = EXCLUDED.rol
        """, ("Ruben", "Admin", "ruben.admin@educonnect.com", admin_pass, "administrador"))

        # 2. Crear Estudiante de prueba - juan.perez@educonnect.com / 9876543
        estudiante_pass = auth.get_password_hash("9876543")
        cursor.execute("""
            INSERT INTO usuarios (nombre, apellido, email, password, rol) 
            VALUES (%s, %s, %s, %s, %s) 
            ON CONFLICT (email) DO UPDATE SET password = EXCLUDED.password
        """, ("Juan", "Perez", "juan.perez@educonnect.com", estudiante_pass, "estudiante"))

        connection.commit()
        print("¡Usuarios creados/actualizados exitosamente!")
        return True
        
    except Exception as e:
        print(f"Error al insertar usuarios: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    seed_users()

