
import flask
from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from sshtunnel import SSHTunnelForwarder
import paramiko

app = Flask(__name__)

# Forzamos a PyMySQL a desviar todo su tráfico a través del túnel proxy
# permitido por PythonAnywhere para cuentas gratuitas.
pymysql.install_as_MySQLdb()


# config database

#app.config["SQL_ALCHEMY_URI"]=f"mysqltpymysql://{os.environ.get('MYSQL_USER')}:{os.environ.get('MYSQL_PASS')}@{os.environ.get('MYSQL_USER')}/{os.environ.get('DB_SERVER_IP')}:{os.environ.get('PORT')}/{os.eviron.get('MYSQL_USER')}"

port_env = os.environ.get('PORT')
db_port = int(port_env) if port_env else 4000

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{os.environ.get('MYSQL_USER')}:{os.environ.get('MYSQL_PASS')}"
    f"@{os.environ.get('DB_SERVER_IP')}:{db_port}/{os.environ.get('DB_NAME')}"
)


TIDB_USER = "e8Jj9F55h2GELMP.root"
TIDB_PASS = "D1EHsdGHS2nJsskD"  # Pon tu contraseña real aquí completa
TIDB_HOST = "gateway01.us-east-1.prod.aws.tidbcloud.com"
TIDB_PORT = 3306
TIDB_NAME = "escuela"

# Generación manual de la URI sin depender de os.environ
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{TIDB_USER}:{TIDB_PASS}@{TIDB_HOST}:{TIDB_PORT}/{TIDB_NAME}"

# Parámetros necesarios para evitar desconexiones en TiDB Cloud
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 300,
    "pool_pre_ping": True
}



'''
# CONFIGURACIÓN MANUAL DIRECTA SIN VARIABLES DE ENTORNO
TIDB_USER = "e8Jj9F55h2GELMP.root"
TIDB_PASS = "D1EHsdGHS2nJsskD"
TIDB_HOST = "://tidbcloud.com"
TIDB_PORT = 4000
TIDB_NAME = "escuela"

if not hasattr(paramiko, 'DSSKey'):
    paramiko.DSSKey = paramiko.PKey

# CONFIGURACIÓN DEL TÚNEL SSH
tunnel = SSHTunnelForwarder(
    (TIDB_HOST, 22),  # TiDB por defecto acepta túneles en el puerto SSH estándar
    ssh_username=TIDB_USER,
    ssh_password=TIDB_PASS,
    remote_bind_address=('127.0.0.1', TIDB_PORT)
)

# Arrancamos el túnel de red
tunnel.start()

# Ahora nos conectamos a nuestro propio puerto local asignado dinámicamente por el túnel
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{TIDB_USER}:{TIDB_PASS}@127.0.0.1:{tunnel.local_bind_port}/{TIDB_NAME}"
'''

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 300,
    "pool_pre_ping": True
}








app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    deleted_at = db.Column(db.DateTime)


#with app.app_context():
#    db.create_all()

@app.route('/')
def hello_world():
    return flask.render_template("index.html")

@app.route('/login', methods=["POST"])
def login():
    try:
        if flask.request.is_json:
            data = flask.request.get_json()
            mail = data.get("email")
            pwd = data.get("password")
        else:
            mail = flask.request.form.get("email")
            pwd = flask.request.form.get("password")
    except Exception as e:
        return flask.jsonify({"Error": str(e)})

    user = User.query.filter_by(email=mail).first()
    if user and user.password == pwd:
        return flask.jsonify({"Success": f"User: {user.email} found"})
    else:
        return flask.jsonify({"Error": "Invalid credentials"})
