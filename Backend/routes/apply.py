from flask import Blueprint, request, jsonify
from models.user import User
from utils.auth import get_user_from_token
from models.applications import Application
from database.connection import Neo4jConnection
import uuid

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

        token = request.headers.get('Authorization').split(' ')[1]
        user_email = get_user_from_token(token)
        if not user_email:
            return jsonify({'error': 'User not found'}), 401

        # Use the Application model to create a new application
        application = Application.create_application(user_email, data)
        if not application:
            return jsonify({'error': 'Failed to create application'}), 500

        return jsonify({
            'message': 'Policy application submitted successfully',
            'application_id': application.application_id
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@apply_bp.route('/update_', methods=['POST'])
def update_application():
    """Update application and link to ClaimManagement node"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        required_fields = ['application_id', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        application_id = data['application_id']
        email = data['email']

        # Generate a unique management ID
        management_id = f"management_{application_id}_{uuid.uuid4()}"

        query = """
        MATCH (u:User {email: $email})
        MATCH (a:Application {application_id: $application_id})
        MERGE (cm:ClaimManagement {id: $management_id})
        MERGE (cm)-[:LINKED_TO]->(a)
        SET a.updated_at = datetime()
        RETURN a, cm
        """

        neo4j = Neo4jConnection()
        result = neo4j.execute_query(query, parameters={
            'application_id': application_id,
            'email': email,
            'management_id': management_id
        })

        if not result:
            return jsonify({'error': 'Failed to update application or link nodes'}), 500

        return jsonify({
            'message': 'Application updated and linked successfully',
            'management_id': management_id
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
