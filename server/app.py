#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/campers', methods=['GET'])
def get_campers():
    campers = Camper.query.all()
    
    camper_data = []
    
    for camper in campers:
        camper_data.append({
            'id': camper.id,
            'name': camper.name,
            'age': camper.age
        })
        
    return jsonify(camper_data), 200


@app.route('/campers/<int:id>', methods=['GET'])
def get_camper_by_id(id):
    camper = Camper.query.get(id)
    if not camper:
        return jsonify({'error': 'Camper not found'}), 404
    
    camper_data = {
        'id': camper.id,
        'name': camper.name,
        'age': camper.age,
        'signups': [{'id': signup.id, 'activity_id': signup.activity_id, 'time': signup.time} for signup in camper.signups]
    }
    return jsonify(camper_data)

@app.route('/campers', methods=['POST'])
def create_camper():
    data = request.get_json()
    
    name = data.get('name')
    age = data.get('age')
    
    errors = []

    #  Checking for name and age
    if not name:
        errors.append('Name is required')
    if not age:
        errors.append('Age is required')
    # serializing the values of name and age
    elif not isinstance(age, int) or age < 8 or age > 18:
        # pushing the errors found in the errors array
        errors.append('Age must be an integer between 8 and 18')

    # Checking for errors and returning 404 if some are found
    if errors:
        return jsonify({'errors': errors}), 400

    # creating a new camper and adding to the database
    camper = Camper(name=name, age=age)
    
    db.session.add(camper)
    db.session.commit()

    return jsonify({
        'id': camper.id,
        'name': camper.name,
        'age': camper.age
    }), 201

@app.route('/campers/<int:id>', methods=['PATCH'])
def update_camper_by_id(id):
    data = request.get_json()
    camper = Camper.query.get(id)
    if not camper:
        return jsonify({'error': 'Camper not found'}), 404

    errors = []

    #  Checking for name and age
    if 'name' in data and not data['name']:
        errors.append('Name cannot be empty')
    if 'age' in data:
        age = data['age']
        # serializing the values of name and age
        if not isinstance(age, int) or age < 8 or age > 18:
            # pushing the errors to the errors array
            errors.append('Age must be an integer between 8 and 18')

    # Checking for errors and returning 404 if some are found
    if errors:
        return jsonify({'errors': ['validation errors']}), 400

    # updating the values and adding them to the db
    if 'name' in data:
        camper.name = data['name']
    if 'age' in data:
        camper.age = data['age']

    db.session.commit()

    return jsonify({
        'id': camper.id,
        'name': camper.name,
        'age': camper.age
    }), 202


@app.route('/activities', methods=['GET'])
def get_activities():
    activities = Activity.query.all()
    
    activities_data = []
    
    for activity in activities:
        activities_data.append({
            'id': activity.id,
            'name': activity.name,
            'difficulty': activity.difficulty
        })
    return jsonify(activities_data)

@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activity_by_id(id):
    activity = Activity.query.get(id)
    
    if not activity:
        return jsonify({'error': 'Activity not found'}), 404
    
    db.session.delete(activity)
    db.session.commit()
    
    return '', 204


@app.route('/signups', methods=['POST'])
def create_signup():
    data = request.get_json()
    # getting the json values
    camper_id = data.get('camper_id')
    activity_id = data.get('activity_id')
    time = data.get('time')

    camper = Camper.query.get(camper_id)
    activity = Activity.query.get(activity_id)
    # checking if the values exist
    if not camper or not activity:
        return jsonify({'error': 'Camper or activity not found'}), 404

    errors = []

    #  serializing the values and adding the errors to the error array if any are found
    if not isinstance(time, int) or time < 0 or time > 23:
        errors.append('Invalid time')

    if errors:
        return jsonify({'errors': ['validation errors']}), 400

    #  Adding new sign up info to the db
    signup = Signup(camper_id=camper_id, activity_id=activity_id, time=time)

    db.session.add(signup)
    db.session.commit()

    return jsonify({
        'id': signup.id,
        'camper_id': signup.camper_id,
        'activity_id': signup.activity_id,
        'activity': {
            'id': activity.id,
            'name': activity.name,
            'difficulty': activity.difficulty
        },
        'camper': {
            'id': camper.id,
            'name': camper.name,
            'age': camper.age
        },
        'time': signup.time
    }), 201


if __name__ == '__main__':
    app.run(port=5555, debug=True)
