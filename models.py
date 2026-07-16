
from flask_sqlalchemy import SQLAlchemy
import enum

db = SQLAlchemy()

class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"

    @classmethod
    def normalize(cls, value):
        if isinstance(value, cls):
            return value
        if value is None:
            return cls.USER
        if isinstance(value, str):
            normalized = value.strip().upper()
            try:
                return cls[normalized]
            except KeyError:
                try:
                    return cls(normalized)
                except ValueError:
                    return cls.USER
        return cls.USER

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum(UserRole),default=UserRole.USER, nullable=False)
    is_aproved =db.Column(db.Boolean,nullable=False,default=False)
    profile_photo= db.Column(db.String(255), nullable=True, default="default.png")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    deleted_at = db.Column(db.DateTime)

    def __init__(self,name,email,password,role=UserRole.USER,profile_photo="default.png", is_aproved=False):
        self.name=name
        self.email=email
        self.password=password
        self.role=UserRole.normalize(role)
        self.is_aproved = False if is_aproved is None else is_aproved
        self.profile_photo=profile_photo

    def __repr__(self):
        return f"<User {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "profile_photo":self.profile_photo,
            "role":self.role.value,
            "is_aproved":self.is_aproved,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None
        }

    def get_attribute(self, attr):
        for a in User.__table__.columns.keys():
            if a.lower() == attr.lower():
                return getattr(self, a)