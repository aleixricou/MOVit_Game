"""
Mòdul de definició de les taules
"""
import datetime
from .basedades import BASEDADES as db
from flask_security import UserMixin, RoleMixin
from flask_security.utils import hash_password


# Definim els rols i les taules

roles_users = db.Table(
    'roles_users',
    db.Column('partida_id', db.Integer(), db.ForeignKey('partida.id')),
    db.Column('cientific_id', db.Integer(), db.ForeignKey('cientific.id')),
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
    )



class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    
class Cientific(db.Model, UserMixin):
    __tablename__ = 'cientific'
    id = db.Column(db.Integer, primary_key=True)
    usuari = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('cientifics', lazy='dynamic'))
    posts = db.relationship('User',backref='author', lazy =True)
    num_usuaris = db.Column(db.Integer)
    
    def set_password(self, password):
        self.password = hash_password(password)
    
    def length(self):
        return len(self.posts)
        
        
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255))
    usuari = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    email_cientific = db.Column(db.String(255), db.ForeignKey('cientific.email'))
    codi = db.Column(db.String(255), unique=True)
    punt_max = db.Column(db.Float(), default=0.0) #Puntuació màxima del jugador
    registrat = db.Column(db.Boolean(), default=False)
    dificulty = db.Column(db.Integer(), default=1)
    level = db.Column(db.Integer(), default=1)
    num_partides = db.Column(db.Integer(), default=0)
    partides = db.relationship('Partida',backref='author', lazy =True)
    last_partida = db.Column(db.String(255))
    login = db.Column(db.PickleType(), default={})
    registre = db.Column(db.PickleType(), default={})
    calibration = db.Column(db.DateTime())
    inici = db.Column(db.PickleType(), default={})
    partides_win = db.Column(db.Integer(), default=0)
      
    def __str__(self):
        return self.email

    def set_password(self, password):
        self.password = hash_password(password)
    
class Partida(db.Model, UserMixin):
    __tablename__ = 'partida'
    id = db.Column(db.Integer, primary_key=True)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('partida', lazy='dynamic'))
    active = db.Column(db.Boolean())
    player = db.Column(db.String(255), db.ForeignKey('user.usuari'))
    current = db.Column(db.Boolean(), default=False) #if player playing == True
    total_points = db.Column(db.Float())
    level_partida = db.Column(db.Integer())
    num_milestones = db.Column(db.Integer())
    difficulty_partida = db.Column(db.Integer())
    rank = db.Column(db.Integer(), default=1)
    pics = db.Column(db.PickleType(), default=[])
    nparades = db.Column(db.Integer(), default=0)
    answer1=db.Column(db.Integer())
    answer2=db.Column(db.Integer())
    answer3=db.Column(db.Integer())
    answer4=db.Column(db.Integer())
    order = db.Column(db.PickleType(), default=[])
    dia_partida = db.Column(db.String(255))

