
import flask
from flask import Flask
from sshtunnel import SSHTunnelForwarder
import paramiko

from config import DevelopmentConfig
from models import db,User

app = Flask(__name__)

# Forzamos a PyMySQL a desviar todo su tráfico a través del túnel proxy
# permitido por PythonAnywhere para cuentas gratuitas.
#pymysql.install_as_MySQLdb()

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

#app.config.from_object(DevelopmentConfig)
db.init_app(app)

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

@app.route('/users', methods=["POST"])
def add_user():
    data = flask.request.get_json()
    if not data:
        return {"Error": "No se proporcionaron datos en formato JSON"}, 400
    name=data.get("name")
    email=data.get("email")
    pwd=data.get("password")
    if not name or not email or not pwd:
        return {"Error": "Faltan campos obligatorios (name, email, password)"}, 400
    try:
        usuario=User(name,email,pwd)
        db.session.add(usuario)
        db.session.commit()
        return {"message":f"successfully added user {name}"},200
    except Exception as e:
        db.session.rollback()
        return {"Error":e},500



@app.route("/users")
def list_users():
    try:
        if flask.request.args.get("filter"):
            db.session.execute(db.select(User).filter_by(User.get_attribute(flask.request.args.get("filter"))==flask.request.args.get("value")))
        else:
            users=User.query.all()
        return {"users":[user.to_dict() for user in users]},200
    except Exception as e:
        return {"Error":str(e)},500

@app.route("/users/<int:id>")
def search_user(id:int):
    try:
        user = User.query.get(id)
        if user:
            return {"user": user.to_dict()}, 200
        else:
            return {"Error": f"User with id {id} not found"}, 404
    except Exception as e:
        return {"Error": str(e)}, 500

@app.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id:int):
    try:
        user = User.query.get(id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return {"message": f"User with id {id} deleted successfully"}, 200
        else:
            return {"Error": f"User with id {id} not found"}, 404
    except Exception as e:
        db.session.rollback()
        return {"Error": str(e)}, 500

@app.route("/users/<int:id>", methods=["PUT"])
def update_user(id:int):
    data = flask.request.get_json()
    try:
        usuario=User.query.get(id)
        if not data:
            return {"Error": "No se proporcionaron datos en formato JSON"}, 400
        name=data.get("name")
        email=data.get("email")
        pwd=data.get("password")
        usuario.name=name if name!=None else usuario.name
        usuario.email=email if email!=None else usuario.email
        usuario.password=pwd if pwd!=None else usuario.password
        db.session.commit()
        return {"message":f"successfully updated user {usuario.name}"},200
    except Exception as e:
        db.session.rollback()
        return {"Error":str(e)},500

#if __name__ == '__main__':
    #with app.app_context():
    #    db.create_all()
#    app.run(debug=True)