from app.database import db, Reading, Sensor, User
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session, abort, jsonify
from flask_bcrypt import Bcrypt
from hashlib import sha256
from datetime import datetime

views = Blueprint('views', __name__)

bcrypt = Bcrypt(current_app)

@views.route('/')
def index():
  if "username" in session:
    user = User.query.filter_by(username=session['username'])
  else:
    user = None
  return render_template("main/index.html", user=user)

@views.route('/register', methods=['GET', 'POST'])
def login():
  if request.method == 'GET':
    return render_template('main/register.html')
  else:
    data = request.get_json()

    if "username" not in data:
      return jsonify({'success' : False})
    if "password" not in data:
      return jsonify({'success' : False})

    if User.query.filter_by(username = data['username']).first():
      return jsonify({'success': False})

    bcrypt_password = bcrypt.generate_password_hash(data['password']).decode()
    
    new_user = User(username = data['username'], password = bcrypt_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success' : True})

@views.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'GET':
    return render_template('main/login.html')
  else:
    data = request.form

    if "username" not in data:
      return jsonify({'success' : False})
    if "password" not in data:
      return jsonify({'success' : False})
    
    user = User.query.filter_by(username=data['username']).first()
    if user == None:
      return jsonify({'success' : False})

    if not bcrypt.check_password_hash(user.password, data['password']):
      return jsonify({'success' : False})
    
    session["username"] = user.username

    return jsonify({'success' : True})

@views.route('/logout')
def logout():
  session.pop('username', None)
  return redirect(url_for('views.index'))

@views.route('/users/token', methods=['POST'])
def user_token():
  data = request.get_json()

  if "username" not in data:
    return jsonify({'success' : False})
  if "password" not in data:
    return jsonify({'success' : False})

  user = User.query.filter_by(username=data['username']).first()
  if user == None:
    return jsonify({'success' : False})

  if not bcrypt.check_password_hash(user.password, data['password']):
    return jsonify({'success' : False})
  
  token = sha256(str(user.id).encode() + current_app.secret_key).hexdigest()

  return jsonify({'success': True, 'token' : token, 'id' : str(user.id)})


@views.route('/users/<user_id>/sensors/create', methods=['POST'])
def create_sensor(user_id):
  data = request.get_json()

  if "token" not in data:
    return jsonify({'success' : False})

  if data['token'] != sha256(user_id.encode() + current_app.secret_key).hexdigest():
    return jsonify({'success' : False})

  user = User.query.filter_by(id=user_id).first()
  if user == None:
    return jsonify({'success' : False})
  
  new_sensor = Sensor(user=user)
  db.session.add(new_sensor)
  db.session.commit()

  token = sha256(str(new_sensor.id).encode() + current_app.secret_key).hexdigest()
  
  return jsonify({'success': True, 'token': token, 'id' : str(new_sensor.id)})

@views.route('/sensors/<sensor_id>/update', methods=['POST'])
def update_sensor(sensor_id):
  data = request.get_json()

  if "token" not in data:
    return jsonify({'success' : False})
  if "value" not in data:
    return jsonify({'success' : False})

  if data['token'] != sha256(sensor_id.encode() + current_app.secret_key).hexdigest():
    return jsonify({'success' : False})

  sensor = Sensor.query.filter_by(id=sensor_id).first()
  
  new_reading = Reading(time=datetime.now(), value=float(data['value']), sensor=sensor)
  db.session.add(new_reading)
  db.session.commit()

  return jsonify({'success': True})


@views.route('/users/<user_id>/sensors', methods=['POST'])
def user_sensors(user_id):
  data = request.get_json()

  if "token" not in data:
    return jsonify({'success' : False})

  if data['token'] != sha256(user_id.encode() + current_app.secret_key).hexdigest():
    return jsonify({'success' : False})
  
  user = User.query.filter_by(id=user_id).first()

  sensors = user.sensors

  return jsonify([s.as_dict() for s in sensors])

@views.route('/users/<user_id>/sensors/<sensor_id>', methods=['POST'])
def user_sensor(user_id, sensor_id):
  data = request.get_json()

  if "token" not in data:
    return jsonify({'success' : False})

  if data['token'] != sha256(user_id.encode() + current_app.secret_key).hexdigest():
    return jsonify({'success' : False})

  sensor = Sensor.query.filter_by(user_id=user_id, id=sensor_id).first()

  if sensor == None:
    return jsonify({'success' : False})
  
  return jsonify(sensor.as_dict_with_readings())
