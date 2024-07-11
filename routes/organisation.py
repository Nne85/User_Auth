from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.organisation import Organisation
from models.user import User
from sqlalchemy.orm import Session

session = Session()
app = Blueprint('organisation', __name__)

@app.route('/organisations', methods=['GET'])
@jwt_required()
def get_organisations():
    userId = get_jwt_identity()
    user = db.session.get(User, userId)
    # org = db.session.get(Organisation, orgId)

    if not user:
        return jsonify({'status': 'Bad request', 'message': 'User not found', 'statusCode': 404})

    all_orgs = set(user.owned_organisations + user.organisations)
    org_list = [{'orgId': str(org.orgId), 'name': org.name, 'description': org.description} for org in all_orgs]

    return jsonify({'status': 'success', 'message': 'Organisations retrieved', 'data': {'organisations': org_list}}), 200


@app.route('/organisations/<orgId>', methods=['GET'])
@jwt_required()
def get_organisation(orgId):
    userId = get_jwt_identity()
    user = db.session.get(User, userId)

    if not user:
        return jsonify({'status': 'Bad request', 'message': 'User not found', 'statusCode': 404})

    org = db.session.get(Organisation, orgId)
    if not org or (org not in user.owned_organisations and org not in user.organisations):
        return jsonify({'status': 'Bad request', 'message': 'Organisation not found or access denied', 'statusCode': 404}), 404

    return jsonify({'status': 'success', 'message': 'Organisation retrieved', 'data': {'orgId': str(org.orgId), 'name': org.name, 'description': org.description}}), 200


@app.route('/organisations', methods=['POST'])
@jwt_required()
def create_organisation():
    data = request.get_json()
    userId = get_jwt_identity()
    user = db.session.get(User, userId)

    if not user:
        return jsonify({'status': 'Bad request', 'message': 'User not found', 'statusCode': 404})

    # Validate data
    if not data.get('name'):
        return jsonify({'errors': [{'field': 'name', 'message': 'Name is required'}]}), 422

    existing_org = Organisation.query.filter_by(name=data['name'], ownerId=userId).first()
    if existing_org:
        return jsonify({'status': 'Bad request', 'message': 'Organisation with this name already exists', 'statusCode': 400})


    new_org = Organisation(
        name=data['name'],
        description=data.get('description'),
        ownerId=userId
    )

    db.session.add(new_org)
    if new_org not in user.organisations:
        user.organisations.append(new_org)
        db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'Organisation created successfully',
        'data': {
            'orgId': str(new_org.orgId),
            'name': new_org.name,
            'description': new_org.description
        }
    }), 201


@app.route('/organisations/<orgId>/users', methods=['POST'])
@jwt_required()
def add_user_to_organisation(orgId):
    data = request.get_json()
    userId = get_jwt_identity()

    logging.info(f"Request by userId: {userId} to add user: {data['userId']} to organisation: {orgId}")

    # Validate user_id
    user = User.query.get(data['userId'])
    if not user:
        logging.error(f"User not found: {data['userId']}")
        return jsonify({'errors': [{'field': 'userId', 'message': 'User not found'}]}), 422

    # Validate organisation
    org = db.session.get(Organisation, orgId)
    if not org:
        logging.error(f"Organisation not found: {orgId}")
        return jsonify({'errors': [{'field': 'userId', 'message': 'User not found'}]}), 422
    logging.info(f"Organisation ownerId: {org.ownerId}")

    if str(org.ownerId) != str(userId):
        logging.error(f"Access denied for userId: {userId} on organisation: {orgId}")
        return jsonify({'status': 'Bad request', 'message': 'Organisation not found or access denied', 'statusCode': 404})

    if org.org.users:
        logging.warning(f"User already in organisation: {orgId}")
        return jsonify({'status': 'Bad request', 'message': 'User already in organisation', 'statusCode': 400})

    if user in org.users:
        logging.warning(f"User already in organisation: {orgId}")
        return jsonify({'status': 'Bad request', 'message': 'User already in organisation', 'statusCode': 400})

    org.users.append(user)
    db.session.commit()

    logging.info(f"User {data['userId']} added to organisation {orgId}")
    return jsonify({'status': 'success', 'message': 'User added to organisation successfully'}), 200

@app.route('/users/<id>', methods=['GET'])
@jwt_required()
def get_user(id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if not current_user:
        return jsonify({'status': 'Bad request', 'message': 'Current user not found', 'statusCode': 404})

    user = User.query.get(id)

    if not user:
        return jsonify({'status': 'Bad request', 'message': 'User not found', 'statusCode': 404})

    # Check if the current user has access to this user's information
    if str(user.userId) != current_user_id and not any(org in current_user.organisations for org in user.organisations):
        return jsonify({'status': 'Bad request', 'message': 'Access denied', 'statusCode': 403})

    return jsonify({
        'status': 'success',
        'message': 'User retrieved successfully',
        'data': {
            'userId': str(user.userId),
            'firstName': user.firstName,
            'lastName': user.lastName,
            'email': user.email,
            'phone': user.phone
        }
    }), 200
