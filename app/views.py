from app.database import db, Reading, Sensor, User
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session, abort, jsonify
from flask_bcrypt import Bcrypt
from hashlib import sha256
from datetime import datetime

views = Blueprint('views', __name__)

bcrypt = Bcrypt(current_app)

FAILED = jsonify({'success' : False})

# --- Frontend Views --- #

@views.route('/')
def index():
  if "username" in session:
    user = User.query.filter_by(username=session['username']).first()
  else:
    user = None
  return render_template("main/index.html", user=user)

@views.route('/register')
def register():
  return render_template('main/register.html')

@views.route('/login')
def login():
  return render_template('main/login.html')

@views.route('/logout')
def logout():
  session.pop('username', None)
  flash("You have been logged out!", "info")
  return redirect(url_for('views.index'))

@views.route('/plants')
def plants():
  if "username" in session:
    user = User.query.filter_by(username=session['username']).first()
  else:
    abort(401)
  
  return render_template('main/plants.html', user=user)

@views.route('/plant/<sensor_id>')
def plant(sensor_id):
  if "username" in session:
    user = User.query.filter_by(username=session['username']).first()
  else:
    abort(401)

  return render_template('main/plant.html', user=user)

# --- End Frontend Views --- #

@views.route('/users/create', methods=['POST'])
def user_create():
  data = request.get_json()

  if not data:
    return FAILED

  if "username" not in data:
    return FAILED
  if "password" not in data:
    return FAILED

  if User.query.filter_by(username = data['username']).first():
    return jsonify({'success': False})

  bcrypt_password = bcrypt.generate_password_hash(data['password']).decode()
  
  new_user = User(username = data['username'], password = bcrypt_password)
  db.session.add(new_user)
  db.session.commit()

  flash("You have successfully registered! Now you can login!", "info")

  return jsonify({'success' : True})

@views.route('/users/authenticate', methods=['POST'])
def user_token():
  data = request.get_json()

  if not data:
    return FAILED
  if "username" not in data:
    return FAILED
  if "password" not in data:
    return FAILED

  user = User.query.filter_by(username=data['username']).first()
  if user == None:
    return FAILED
  
  if not bcrypt.check_password_hash(user.password, data['password']):
    return FAILED
  
  if "token" in data and data['token']:
    token = sha256(str(user.id).encode() + current_app.secret_key).hexdigest()
    return jsonify({'success': True, 'token' : token, 'id' : str(user.id)})
  else:    
    session["username"] = user.username
    flash("You have been logged in!", "info")
    return jsonify({'success' : True})

@views.route('/users/<user_id>/sensors/create', methods=['POST'])
def create_sensor(user_id):
  data = request.get_json()

  if "token" not in data:
    return FAILED

  if data['token'] != sha256(user_id.encode() + current_app.secret_key).hexdigest():
    return FAILED

  user = User.query.filter_by(id=user_id).first()
  if user == None:
    return FAILED
  
  new_sensor = Sensor(user=user)
  db.session.add(new_sensor)
  db.session.commit()

  token = sha256(str(new_sensor.id).encode() + current_app.secret_key).hexdigest()
  
  return jsonify({'success': True, 'token': token, 'id' : str(new_sensor.id)})

@views.route('/sensors/<sensor_id>/update', methods=['POST'])
def update_sensor(sensor_id):
  data = request.get_json()

  if "token" not in data:
    return FAILED
  if "value" not in data:
    return FAILED

  if data['token'] != sha256(sensor_id.encode() + current_app.secret_key).hexdigest():
    return FAILED

  sensor = Sensor.query.filter_by(id=sensor_id).first()
  
  new_reading = Reading(time=datetime.now(), value=float(data['value']), sensor=sensor)
  db.session.add(new_reading)
  db.session.commit()

  return jsonify({'success': True})


@views.route('/users/<user_id>/sensors', methods=['GET','POST'])
def user_sensors(user_id):
  if request.method == 'GET':
    if "username" in session:
      user = User.query.filter_by(username=session['username']).first()

      if user == None:
        return FAILED
      if str(user.id) != user_id:
        return FAILED
    else:
      return FAILED
  else:
    data = request.get_json()
    if "token" not in data:
      return FAILED
    if data['token'] != sha256(user_id.encode() + current_app.secret_key).hexdigest():
      return FAILED
    user = User.query.filter_by(id=user_id).first()
    if user == None:
      return FAILED
  sensors = user.sensors
  return jsonify([s.as_dict() for s in sensors])

@views.route('/users/<user_id>/sensors/<sensor_id>', methods=['GET','POST'])
def user_sensor(user_id, sensor_id):
  if request.method == 'GET':
    if "username" in session:
      user = User.query.filter_by(username=session['username']).first()
      if str(user.id) != user_id:
        return FAILED
    else:
      return FAILED
  else:
    data = request.get_json()
    if "token" not in data:
      return FAILED
    if data['token'] != sha256(user_id.encode() + current_app.secret_key).hexdigest():
      return FAILED
    sensor = Sensor.query.filter_by(user_id=user_id, id=sensor_id).first()
  if sensor == None:
    return FAILED
  return jsonify(sensor.as_dict_with_readings())
