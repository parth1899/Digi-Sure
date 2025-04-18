import secrets
import string
import bcrypt
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
            # Instead of passing the User object, we'll pass just the email
            current_user_email = data['email']
            if not current_user_email:
                return jsonify({'message': 'Invalid token'}), 401
            return f(current_user_email, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
    return decorated


def get_user_from_token(token):
    try:
        payload = decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload.get('email')
    except Exception as e:
        print(f"Token decode error: {str(e)}")
        return None

def generate_strong_password():
    letters = string.ascii_letters
    digits = string.digits
    special_chars = "!@#$%^&*"
    all_chars = letters + digits + special_chars

    password = ''.join(secrets.choice(letters) for _ in range(2))
    password += ''.join(secrets.choice(digits) for _ in range(2))
    password += ''.join(secrets.choice(special_chars) for _ in range(2))
    password += ''.join(secrets.choice(all_chars) for _ in range(6))

    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)
    return ''.join(password_list)