import jwt
from jwt import decode
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from config import Config

def create_token(user_email):
    """Create a JWT token for the user"""
    payload = {
        'email': user_email,
        'exp': datetime.utcnow() + timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')

def token_required(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            token = token.split()[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            from models.user import User
            current_user = User.get_user_by_email(data['email'])
            if not current_user:
                return jsonify({'message': 'Invalid token'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated


def get_user_from_token(token):
    try:
        payload = decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload.get('email')
    except Exception as e:
        print(f"Token decode error: {str(e)}")
        return None