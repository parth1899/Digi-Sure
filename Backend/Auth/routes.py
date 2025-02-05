from flask import Blueprint, request, jsonify
import jwt
from datetime import datetime, timedelta
from functools import wraps
from Models.user import User
from config import Config

auth_bp = Blueprint('auth', __name__)

def create_token(user_email):
    payload = {
        'email': user_email,
        'exp': datetime.utcnow() + timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            token = token.split()[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            current_user = User.get_user_by_email(data['email'])
            if not current_user:
                return jsonify({'message': 'Invalid token'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
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
    # In a more complete implementation, you might want to blacklist the token
    return jsonify({'message': 'Successfully signed out'})