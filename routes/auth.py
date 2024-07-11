
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required
from app import db
from datetime import datetime, timedelta
from models.user import User
from models.organisation import Organisation

app = Blueprint('auth', __name__)

@app.route('/register', methods=['POST'])
def register():
    """This function handles the user registration and validates data. """
    data = request.get_json()
    errors = []
    if not data.get('firstName'):
        errors.append({'field': 'firstName', 'message': 'First name is required'})
    if not data.get('lastName'):
        errors.append({'field': 'lastName', 'message': 'Last name is required'})
    if not data.get('email'):
        errors.append({'field': 'email', 'message': 'Email is required'})
    if not data.get('password'):
        errors.append({'field': 'password', 'message': 'Password is required'})

    if errors:
        return jsonify({'errors': errors}), 422                                                 
    # Check for existing user
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'status': 'Bad request', 'message': 'Registration unsuccessful', 'errors': [{'field': 'email', 'message': 'Email already exists'}], 'statusCode': 400}), 400

    # Create new user
    new_user = User(
        firstName=data['firstName'],
        lastName=data['lastName'],
        email=data['email'],
        password=generate_password_hash(data['password']),
        phone=data.get('phone')
    )

    db.session.add(new_user)
    db.session.flush()

    # Create default organisation
    new_org = Organisation(
        name=f"{data['firstName']}'s Organisation",
        ownerId=new_user.userId
    )

    db.session.add(new_org)
    new_user.organisations.append(new_org)
    db.session.commit()

    # Generate access token
    access_token = create_access_token(identity=str(new_user.userId))

    return jsonify({
        'status': 'success',
        'message': 'Registration successful',
        'data': {
            'accessToken': access_token,
            'user': {
                'userId': str(new_user.userId),
                'firstName': new_user.firstName,
                'lastName': new_user.lastName,
                'email': new_user.email,
                'phone': new_user.phone
            }
        }
    }), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'status': 'Bad request', 'message': 'Authentication failed', 'statusCode': 401}), 401

    access_token = create_access_token(identity=user.userId)

    return jsonify({
        'status': 'success',
        'message': 'Login successful',
        'data': {
            'accessToken': access_token,
            'user': {
                'userId': str(user.userId),
                'firstName': user.firstName,
                'lastName': user.lastName,
                'email': user.email,
                'phone': user.phone
            }
        }
    }), 200
