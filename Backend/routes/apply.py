from tokenize import TokenError
from flask import Blueprint, request, jsonify
from models.user import User
from utils.auth import get_user_from_token
from models.applications import Application

apply_bp = Blueprint('apply', __name__)

@apply_bp.route('/new', methods=['POST'])
def apply():
    """Apply the policy details"""

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        required_fields = [
            'vehicleType', 'registrationNumber', 'make', 'model', 'year',
            'name', 'mobile', 'email', 'address', 'city', 'state',
            'idv', 'ncb', 'addons', 'policy_annual_premium', 'umbrella_limit', 
            'policy_csl', 'total_insurance_amount'
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # token = request.headers.get('Authorization')
        token = request.headers.get('Authorization').split(' ')[1]
        user_email = get_user_from_token(token)
        if not user_email:
            return jsonify({'error': 'User not found'}), 401

        # creating the new policy application
        application = Application.create_application(user_email, data)
        if not application:
            return jsonify({'error': 'Failed to create application'}), 500
        
        return jsonify({
            'message': 'Policy application submitted successfully',
            'application_id': application.application_id
        }), 201

    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
