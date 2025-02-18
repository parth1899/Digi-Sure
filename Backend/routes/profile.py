import os
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from utils.auth import token_required, get_user_from_token
from database.connection import Neo4jConnection 
from config import Config
from models.profile import Profile

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/update-profile', methods=['POST'])
@token_required
def update_profile(current_user):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        required_fields = [
            'name', 'phone', 'customerId', 'address',
            'bankingDetails'
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Validate banking details
        banking_fields = ['aadharNumber', 'panNumber', 'accountNumber', 'ifscCode']
        for field in banking_fields:
            if field not in data['bankingDetails']:
                return jsonify({'error': f'Missing banking field: {field}'}), 400

        # Get user email from the User object
        user_email = current_user.email

        # Update the profile
        profile = Profile.update_profile(user_email, data)
        if not profile:
            return jsonify({'error': 'Failed to update profile'}), 500
        
        # Convert the response to a dictionary
        response_data = {
            'message': 'Profile updated successfully',
            'data': {
                'email': profile.email,
                'name': profile.name,
                'phone': profile.phone,
                'customerId': profile.customer_id,
                'address': profile.address,
                'bankingDetails': profile.banking_details
            }
        }
        
        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/get-profile', methods=['GET'])
@token_required
def get_profile(current_user):
    try:
        user_email = current_user.email

        profile = Profile.get_profile(user_email)
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404

        return jsonify({
            'data': {
                'email': profile.email,
                'name': profile.name,
                'phone': profile.phone,
                'customerId': profile.customer_id,
                'address': profile.address,
                'bankingDetails': profile.banking_details
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500