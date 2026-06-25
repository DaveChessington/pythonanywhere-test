import os

# config database

#app.config["SQL_ALCHEMY_URI"]=f"mysqltpymysql://{os.environ.get('MYSQL_USER')}:{os.environ.get('MYSQL_PASS')}@{os.environ.get('MYSQL_USER')}/{os.environ.get('DB_SERVER_IP')}:{os.environ.get('PORT')}/{os.eviron.get('MYSQL_USER')}"

class DevelopmentConfig:
    port_env = os.environ.get('PORT')
    db_port = int(port_env) if port_env else 4000

    '''SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.environ.get('MYSQL_USER')}:{os.environ.get('MYSQL_PASS')}"+
        f"@{os.environ.get('DB_SERVER_IP')}:{db_port}/{os.environ.get('DB_NAME')}"
    )'''

    SQLALCHEMY_DATABASE_URI = ("sqlite:///escuela.db")

    # Parámetros necesarios para evitar desconexiones en TiDB Cloud
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER=os.environ.get("UPLOAD_FOLDER")