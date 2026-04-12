import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def seed_data():
    try:
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            connection = psycopg2.connect(db_url)
        else:
            connection = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "root"),
                dbname=os.getenv("DB_NAME", "educonnect_ruben")
            )
        
        cursor = connection.cursor()

        # Check if modules already exist to avoid duplication
        cursor.execute("SELECT COUNT(*) FROM modulos")
        if cursor.fetchone()[0] > 0:
            print("Los módulos ya existen en la base de datos. Saltando siembra...")
            return

        modulos_data = [
            ("Taller de Sistemas Operativos I", "Técnico Básico", ""),
            ("Matemática para la Informática", "Técnico Básico", ""),
            ("Programación I-A", "Técnico Básico", ""),
            ("Hardware de Computadoras I", "Técnico Básico", ""),
            ("Emergente", "Técnico Básico", ""),
            ("Taller de Sistemas Operativos II", "Técnico Auxiliar", ""),
            ("Ofimática y Tecnología Multimedia I", "Técnico Auxiliar", ""),
            ("Programación I-B", "Técnico Auxiliar", ""),
            ("Hardware de Computadoras II", "Técnico Auxiliar", ""),
            ("Emergente", "Técnico Auxiliar", ""),
            ("Inglés Técnico", "Técnico Medio I", "Nivel Medio"),
            ("Diseño y Programación Web I-A", "Técnico Medio I", "Nivel Medio"),
            ("Programación I-C", "Técnico Medio I", "Nivel Medio"),
            ("Ofimática y Tecnología Multimedia II", "Técnico Medio I", "Nivel Medio"),
            ("Emprendimiento Productivo", "Técnico Medio I", "Nivel Medio"),
            ("Redes de Computadoras I", "Técnico Medio II", "Nivel Medio"),
            ("Diseño y Programación Web I-B", "Técnico Medio II", "Nivel Medio"),
            ("Base de Datos I", "Técnico Medio II", "Nivel Medio"),
            ("Programación Móvil I", "Técnico Medio II", "Nivel Medio"),
            ("Modalidades de Graduación", "Técnico Medio II", "Nivel Medio"),
        ]

        print("Insertando 20 módulos...")
        for mod in modulos_data:
            cursor.execute("INSERT INTO modulos (nombre, nivel, subnivel) VALUES (%s, %s, %s) RETURNING id", mod)
            mod_id = cursor.fetchone()[0]
            
            # Crear contenidos vacíos para cada módulo preparados para recibir URL
            contenidos = [
                (mod_id, "teoria", "Documento de Teoría PDF", ""),
                (mod_id, "video", "Enlace a Video Clase", ""),
                (mod_id, "audio", "Pista de Audio Explicativa", ""),
                (mod_id, "presentacion", "Diapositivas", ""),
                (mod_id, "evaluacion", "Link a la Evaluación", ""),
            ]
            for cont in contenidos:
                cursor.execute("INSERT INTO contenidos (modulo_id, tipo, titulo, url) VALUES (%s, %s, %s, %s)", cont)
        
        connection.commit()
        print("¡Módulos y plantillas de contenido pre-creados con éxito!")

    except Exception as e:
        print(f"Error al sembrar datos: {e}")
    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    seed_data()
