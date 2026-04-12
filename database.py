import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        # En Render, la variable de entorno generada para BD es DATABASE_URL
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
        return connection
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def init_db():
    connection = get_db_connection()
    if not connection:
        print("Couldn't connect to initialize tables")
        return
        
    try:
        cursor = connection.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                rol VARCHAR(20) NOT NULL DEFAULT 'estudiante'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS modulos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(200) NOT NULL,
                nivel VARCHAR(100) NOT NULL,
                subnivel VARCHAR(100)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contenidos (
                id SERIAL PRIMARY KEY,
                modulo_id INT NOT NULL,
                tipo VARCHAR(50) NOT NULL,
                titulo VARCHAR(200) NOT NULL,
                url TEXT NOT NULL,
                FOREIGN KEY (modulo_id) REFERENCES modulos(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluaciones (
                id SERIAL PRIMARY KEY,
                modulo_id INT NOT NULL,
                pregunta TEXT NOT NULL,
                opciones JSONB NOT NULL,
                respuesta_correcta VARCHAR(200) NOT NULL,
                FOREIGN KEY (modulo_id) REFERENCES modulos(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progreso (
                id SERIAL PRIMARY KEY,
                usuario_id INT NOT NULL,
                modulo_id INT NOT NULL,
                estado VARCHAR(50) DEFAULT 'bloqueado',
                nota DECIMAL(5, 2),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (modulo_id) REFERENCES modulos(id) ON DELETE CASCADE,
                UNIQUE (usuario_id, modulo_id)
            )
        ''')
        
        connection.commit()
        print("Tablas de PostgreSQL creadas exitosamente.")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    init_db()
