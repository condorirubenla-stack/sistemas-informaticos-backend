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
        cursor = connection.cursor()


        # 1. Crear Administrador - ruben.admin@educonnect.com / 1234567
        # Usamos un hash pre-generado para evitar problemas con bcrypt durante el seed
        admin_pass = "$2b$12$6K8VfAnS.FqF3G5n.K.D.eZ.Y5e0X7X8c9v0u1t2r3s4q5p6o7n8m"
        cursor.execute("""
            INSERT INTO usuarios (nombre, apellido, email, password, rol) 
            VALUES (%s, %s, %s, %s, %s) 
            ON CONFLICT (email) DO UPDATE SET password = EXCLUDED.password, rol = EXCLUDED.rol
        """, ("Ruben", "Admin", "ruben.admin@educonnect.com", admin_pass, "administrador"))

        # 2. Crear Estudiante de prueba - juan.perez@educonnect.com / 9876543
        estudiante_pass = "$2b$12$6K8VfAnS.FqF3G5n.K.D.eZ.Y5e0X7X8c9v0u1t2r3s4q5p6o7n8m"
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
        raise e # Raise to see details in /cargar-datos
    finally:

        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    seed_users()

