import psycopg2

def main():
    try:
        conn = psycopg2.connect(
            host="host.docker.internal",  # 👈 importante para acceder a tu PC desde Docker Desktop
            port=5433,                    # el puerto de tu Postgres local
            database="utea",      # cambia por el nombre de tu DB
            user="postgres",              # tu usuario
            password="77663540"        # tu contraseña
        )
        print("✅ Conexión exitosa a PostgreSQL")
        conn.close()
    except Exception as e:
        print("❌ Error de conexión:", e)

if __name__ == "__main__":
    main()
