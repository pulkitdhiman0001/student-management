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

    def __init__(self, username, password):
        self.username = username
        self.password = password


class Student(db.Model):
    __tablename__ = "student"

    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    mother_name = db.Column(db.String(100))
    father_name = db.Column(db.String(100))
    addr = db.Column(db.String(100))
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    city = db.relationship('City')
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'))
    state = db.relationship('State')
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
    country = db.relationship('Country')
    pin = db.Column(db.String(100))
    standard_id = db.Column(db.Integer, db.ForeignKey('standard.id'))
    standard = db.relationship('Standard')
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
    section = db.relationship('Section')
    roll_no = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, fname, lname, mother_name, father_name, addr, city_id, state_id, country_id, pin, standard_id,
                 section_id, roll_no, email):
        self.fname = fname
        self.lname = lname
        self.mother_name = mother_name
        self.father_name = father_name
        self.addr = addr
        self.city_id = city_id
        self.state_id = state_id
        self.country_id = country_id
        self.pin = pin
        self.standard_id = standard_id
        self.section_id = section_id
        self.roll_no = roll_no
        self.email = email


class Country(db.Model):
    __tablename__ = "country"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name):
        self.name = name


class State(db.Model):
    __tablename__ = "state"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
    country = db.relationship('Country')

    def __init__(self, name, country_id):
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

    def __init__(self, name, state_id, country_id):
        self.name = name
        self.state_id = state_id
        self.country_id = country_id


class Standard(db.Model):
    __tablename__ = "standard"
    id = db.Column(db.Integer, primary_key=True)
    standard_name = db.Column(db.String(100))

    def __init__(self, standard_name):
        self.standard_name = standard_name


class Section(db.Model):
    __tablename__ = "section"
    id = db.Column(db.Integer, primary_key=True)
    section_name = db.Column(db.String(100))

    def __init__(self, section_name):
        self.section_name = section_name
