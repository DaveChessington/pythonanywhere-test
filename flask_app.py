
# A very simple Flask Hello World app for you to get started with...
import flask
from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# config database
app.config["SQL_ALCHEMY_URI"]=f"mysqltpymysql://{os.environ.get('MYSQL_USER')}:{os.environ.get('MYSQL_PASS')}@{os.environ.get('MYSQL_USER')}ip_publica:purerto/{os.eviron.get('MYSQL_USER')}"

db=SQLAlchemy(app)

# Create user table model
class User(db.Model):
    __tablename__='user'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    name=db.Column(db.String(30),nullable=False)
    email=db.Column(db.String(100),unique=True,nullable=False)
    password=db.Column(db.String(128),nullable=False)
    created_at=db.Column(db.DateTime,default=db.func.current_timestamp())
    updated_at=db.Column(db.DateTime,default=db.func.current_timestamp())
    deleted_at=db.Column(db.Datetime)

@app.route('/')
def hello_world():
#    return 'Hello from Flask!'
	return flask.render_template("index.html")
