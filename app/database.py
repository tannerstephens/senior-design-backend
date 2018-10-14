from flask_sqlalchemy import SQLAlchemy
from flask import current_app

db = SQLAlchemy(current_app)

class Reading(db.Model):
  __tablename__ = "readings"

  id = db.Column(db.Integer, primary_key=True)
  time = db.Column(db.DateTime)
  value = db.Column(db.Float)

  sensor_id = db.Column(db.Integer, db.ForeignKey("sensors.id")) 

class Sensor(db.Model):
  __tablename__ = "sensors"

  id = db.Column(db.Integer, primary_key=True)
  readings = db.relationship("Reading", backref=db.backref('sensor', remote_side=[id]))

  user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

class User(db.Model):
  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(30), unique=True, nullable=False)
  password = db.Column(db.String(60), nullable=False)

  sensors = db.relationship("Sensor", backref=db.backref('user', remote_side=[id]))
