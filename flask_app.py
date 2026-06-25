import os

import flask
from flask import Flask
from flask_migrate import Migrate
from config import DevelopmentConfig
from models import db,User
import datetime

app = Flask(__name__)

app.config.from_object(DevelopmentConfig)

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
        filtro_columna = flask.request.args.get("filter")
        filtro_valor = flask.request.args.get("value")
        if filtro_columna and filtro_valor:
            filtro=getattr(User, filtro_columna)
            if isinstance(filtro.type,(db.DateTime, db.Date)):
                try:
                    filtro_valor = datetime.datetime.strptime(filtro_valor, "%Y-%m-%dT%H:%M:%S")
                    users = User.query.filter(filtro == filtro_valor).all()
                except ValueError:
                        fecha_inicio = datetime.datetime.strptime(filtro_valor, "%Y-%m-%d")
                        fecha_fin = fecha_inicio + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)
                        
                        users = User.query.filter(filtro.between(fecha_inicio, fecha_fin)).all()
            else:
                users = User.query.filter(filtro == filtro_valor).all()
        else:
            users = User.query.all()
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
            pic=os.path.join(app.config['UPLOAD_FOLDER'],user.profile_photo)
            db.session.delete(user)
            db.session.commit()
            if os.path.exists(pic):
                os.remove(pic)
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
    
@app.route("/users/profile_photo/<int:id>")
def get_pic(id:int):
    user = User.query.get(id)
    if user:
        try:
            print(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'],user.profile_photo)))
            return flask.send_from_directory(app.config['UPLOAD_FOLDER'], user.profile_photo)
        except Exception as e:
            print(e)
            return {"Error": "Image not found"}, 404
    return {"Error": "user not found"}, 404

    
@app.route("/users/profile_photo/<int:id>", methods=["POST"])
def update_pic(id:int):
    user = User.query.get(id)
    if not user:
        return {"Error": f"User with id {id} not found"}, 404
    if 'photo' not in flask.request.files:
        return {'error': 'invalid image'}, 400
    file = flask.request.files['photo']
    if file:
        extension = os.path.splitext(file.filename)[1]
        new_name=f"user_{id}{extension}"
        save_route = os.path.join(app.config['UPLOAD_FOLDER'], new_name)
        file.save(save_route)

        user.profile_photo = new_name
        db.session.commit()
        return {"message": f"Profile photo updated for user {user.name}"}, 200

db.init_app(app)

migrate = Migrate(app, db,compare_type=True)


if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating database tables: {e}")
    app.run(debug=True)
