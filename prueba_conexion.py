import pymysql
from sshtunnel import SSHTunnelForwarder

# 1. CONFIGURACIÓN DEL TÚNEL SSH
# PythonAnywhere se conecta a tu CentOS usando la IP pública y el usuario del sistema
with SSHTunnelForwarder(
    ('189.253.18.91', 22),              # IP pública de CentOS y puerto SSH estándar
    ssh_username="rgallegos",                 # El usuario que creaste en CentOS
    ssh_pkey="/home/davechessington/.ssh/id_rsa", # Ruta exacta de tu llave privada
    remote_bind_address=('127.0.0.1', 3306)        # MySQL en CentOS responderá localmente
) as tunnel:

    print("✔ Túnel SSH establecido con éxito.")

    # 2. CONFIGURACIÓN DE LA CONEXIÓN A MYSQL
    # Una vez abierto el túnel, la conexión a MySQL se realiza de forma local
    connection = pymysql.connect(
        host='127.0.0.1',
        port=tunnel.local_bind_port,              # Puerto aleatorio temporal asignado por el túnel
        user='ico901',                  # El usuario de MySQL con permisos en 127.0.0.1
        password='ico901',
        database='test'
    )

    try:
        with connection.cursor() as cursor:
            # Ejecuta una consulta simple para verificar la conexión
            cursor.execute("SELECT VERSION();")
            version = cursor.fetchone()
            print(f"✔ ¡Conexión a MySQL exitosa! Versión del servidor: {version[0]}")

    finally:
        connection.close()
        print("✔ Conexión a la base de datos cerrada limpiamente.")
