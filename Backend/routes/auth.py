from flask import Blueprint, request, jsonify
from models.user import User
from utils.auth import create_token, token_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    required_fields = ['email', 'name', 'surname', 'password']
    
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400

    user = User.create_user(
        data['email'],
        data['name'],
        data['surname'],
        data['password']
    )

    if not user:
        return jsonify({'message': 'User already exists'}), 409

    token = create_token(user.email)
    return jsonify({
        'message': 'User created successfully',
        'token': token
    }), 201

@auth_bp.route('/sign-in', methods=['POST'])
def sign_in():
    """Sign in an existing user"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400

    user = User.get_user_by_email(data['email'])
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401

    token = create_token(user.email)
    return jsonify({
        'message': 'Successfully signed in',
        'token': token
    })

@auth_bp.route('/sign-out', methods=['POST'])
@token_required
def sign_out(current_user):
    """Sign out the current user"""
    return jsonify({'message': 'Successfully signed out'})