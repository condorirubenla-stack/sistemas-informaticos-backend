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

        # Recogemos todos los módulos actuales
        cursor.execute("SELECT id, nombre FROM modulos")
        modulos = cursor.fetchall()

        TIPOS = ["teoria", "video", "audio", "presentacion", "evaluacion"]
        reparados = 0

        for m_id, m_nombre in modulos:
            # Para cada módulo, aseguramos 4 temas × 5 tipos
            for tema_num in range(1, 5):
                for tipo in TIPOS:
                    cursor.execute(
                        "SELECT id FROM contenidos WHERE modulo_id = %s AND tema_num = %s AND tipo = %s",
                        (m_id, tema_num, tipo)
                    )
                    if not cursor.fetchone():
                        cursor.execute(
                            "INSERT INTO contenidos (modulo_id, tipo, titulo, url, tema_num) VALUES (%s,%s,%s,%s,%s)",
                            (m_id, tipo, f"Tema {tema_num} - {tipo.capitalize()}", "", tema_num)
                        )
                        reparados += 1

        connection.commit()
        return reparados
    except Exception as e:
        print(f"Error: {e}")
        return 0

    finally:
        if 'connection' in locals() and connection:
            cursor.close(); connection.close()

if __name__ == "__main__":
    seed_data()
