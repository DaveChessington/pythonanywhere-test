
from flask_sqlalchemy import SQLAlchemy
 
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    deleted_at = db.Column(db.DateTime)

    def __init__(self,name,email,password):
        self.name=name
        self.email=email
        self.password=password

    def __repr__(self):
        return f"<User {self.name}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None
        }
    
    def get_attribute(self, attr):
        for a in User.__table__.columns.keys():
            if a.lower() == attr.lower():
                return getattr(self, a)