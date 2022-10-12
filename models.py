from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "hello"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'

db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)


class Users(db.Model):
    __talename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    confirm_password = db.Column(db.String(100))

    def __init__(self, username, password, confirm_password):
        self.username = username
        self.password = password
        self.confirm_password = confirm_password


class Student(db.Model):
    __tablename__ = "student"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    addr = db.Column(db.String(100))
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    city = db.relationship('City')
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'))
    state = db.relationship('State')
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
    country = db.relationship('Country')
    pin = db.Column(db.String(100))
    standard = db.Column(db.String(100))
    roll_no = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, name, addr, city_id, state_id, country_id, pin, standard, roll_no, email):
        self.name = name
        self.addr = addr
        self.city_id = city_id
        self.state_id = state_id
        self.country_id = country_id
        self.pin = pin
        self.standard = standard
        self.roll_no = roll_no
        self.email = email


class Country(db.Model):
    __tablename__ = "country"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __int__(self, name):
        self.name = name


class State(db.Model):
    __tablename__ = "state"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
    country = db.relationship('Country')

    def __int__(self, name, country_id):
        self.name = name
        self.country_id = country_id


class City(db.Model):
    __tablename__ = "city"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'))
    state = db.relationship('State')
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
    country = db.relationship('Country')

    def __int__(self, name, state_id, country_id):
        self.name = name
        self.state_id = state_id
        self.country_id = country_id
