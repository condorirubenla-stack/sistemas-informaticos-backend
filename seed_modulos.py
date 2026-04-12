import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def seed_data():
    try:
        db_url = os.getenv("DATABASE_URL")
        connection = psycopg2.connect(db_url) if db_url else psycopg2.connect(
            host=os.getenv("DB_HOST","localhost"), user=os.getenv("DB_USER","postgres"),
            password=os.getenv("DB_PASSWORD","root"), dbname=os.getenv("DB_NAME","educonnect_ruben")
        )
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM modulos")
        if cursor.fetchone()[0] > 0:
            print("Módulos ya existen.")
            cursor.close(); connection.close(); return

        modulos_data = [
            ("Taller de Sistemas Operativos I",    "Técnico Básico",   ""),
            ("Matemática para la Informática",      "Técnico Básico",   ""),
            ("Programación I-A",                   "Técnico Básico",   ""),
            ("Hardware de Computadoras I",         "Técnico Básico",   ""),
            ("Emergente I",                        "Técnico Básico",   ""),
            ("Taller de Sistemas Operativos II",   "Técnico Auxiliar", ""),
            ("Ofimática y Tecnología Multimedia I","Técnico Auxiliar", ""),
            ("Programación I-B",                   "Técnico Auxiliar", ""),
            ("Hardware de Computadoras II",        "Técnico Auxiliar", ""),
            ("Emergente II",                       "Técnico Auxiliar", ""),
            ("Inglés Técnico",                     "Técnico Medio I",  ""),
            ("Diseño y Programación Web I-A",      "Técnico Medio I",  ""),
            ("Programación I-C",                   "Técnico Medio I",  ""),
            ("Ofimática y Tecnología Multimedia II","Técnico Medio I", ""),
            ("Emprendimiento Productivo",           "Técnico Medio I",  ""),
            ("Redes de Computadoras I",            "Técnico Medio II", ""),
            ("Diseño y Programación Web I-B",      "Técnico Medio II", ""),
            ("Base de Datos I",                    "Técnico Medio II", ""),
            ("Programación Móvil I",               "Técnico Medio II", ""),
            ("Modalidades de Graduación",          "Técnico Medio II", ""),
        ]

        TIPOS = ["teoria", "video", "audio", "presentacion", "evaluacion"]

        for orden, mod in enumerate(modulos_data, start=1):
            cursor.execute(
                "INSERT INTO modulos (nombre, nivel, subnivel, orden) VALUES (%s,%s,%s,%s) RETURNING id",
                (mod[0], mod[1], mod[2], orden)
            )
            mod_id = cursor.fetchone()[0]

            # 4 temas × 5 tipos de material = 20 contenidos por módulo
            for tema_num in range(1, 5):
                for tipo in TIPOS:
                    cursor.execute(
                        "INSERT INTO contenidos (modulo_id, tipo, titulo, url, tema_num) VALUES (%s,%s,%s,%s,%s)",
                        (mod_id, tipo, f"Tema {tema_num} - {tipo.capitalize()}", "", tema_num)
                    )

        connection.commit()
        print("¡20 módulos con 4 temas cada uno creados!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'connection' in locals() and connection:
            cursor.close(); connection.close()

if __name__ == "__main__":
    seed_data()
