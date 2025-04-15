from utils.auth import encrypt_password, generate_strong_password
import datetime
import json
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


def generate_customer_id():
    unique_id = str(uuid.uuid4()).upper().replace('-', '')
    return f"CUS-{unique_id[:4]}-{unique_id[4:8]}-{unique_id[8:12]}"

@apply_bp.route('/update_policy', methods=['POST'])
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

        neo4j = Neo4jConnection()

        email = data['email']

        # Generate a unique management ID
        management_id = f"management_{email}_{uuid.uuid4()}"

        with neo4j.get_session() as session:
            try:
                # Store all properties as flat key-value pairs
                user_check_query = """
                MATCH (u:User {email: $email})
                RETURN u
                """

                user_result = neo4j.execute_query(user_check_query, {'email': email})
                print(user_result)

                if not user_result:
                    new_password = generate_strong_password()
                    encrypted_password = encrypt_password(new_password)
                    customer_id = generate_customer_id()

                    create_user_query = """
                    CREATE (u:User {
                        email: $email,
                        name: $name,
                        mobile: $mobile,
                        address: $address,
                        created_at: $created_at,
                        customerId: $customerId,
                        password_hash: $password_hash
                    })
                    RETURN u
                    """

                    user_data = {
                        'email': email,
                        'name': data.get('applicant_name', 'Unknown User'),
                        'mobile': data.get('mobile', '0000000000'),
                        'address': data.get('address', 'Unknown Address'),
                        'created_at': datetime.datetime.now().isoformat(),
                        'customerId': customer_id,
                        'password_hash': encrypted_password
                    }

                    user_result = neo4j.execute_query(create_user_query, user_data)
                    print(user_result)

                application_data = {
                    "application_id": data.get("application_id", "Unknown"),
                    "status": data.get("status", "Pending"),
                    # Vehicle details
                    "vehicle_type": data.get("vehicle_type", "Unknown"),
                    "registration_number": data.get("registration_number", "Unknown"),
                    "make": data.get("make", "Unknown"),
                    "model": data.get("model", "Unknown"),
                    "year": data.get("year", "Unknown"),
                    # Personal info
                    "applicant_name": data.get("applicant_name", "Unknown"),
                    "mobile": data.get("mobile", "0000000000"),
                    "email": data.get("email", "Unknown"),
                    "address": data.get("address", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "state": data.get("state", "Unknown"),
                    # Policy details
                    "idv": data.get("idv", 0),
                    "ncb": data.get("ncb", 0),
                    "addons": json.dumps(data.get("addons", [])),  # Convert list to JSON string
                    "policy_annual_premium": data.get("policy_annual_premium", 0),
                    "umbrella_limit": data.get("umbrella_limit", 0),
                    "policy_csl": data.get("policy_csl", 0),
                    "total_insurance_amount": data.get("total_insurance_amount", 0),
                    # Timestamps
                    "created_at": data.get("created_at", datetime.datetime.now().isoformat())
                }

                query = """
                    MATCH (u:User {email: $email})
                    CREATE (a:Application)
                    SET a = $application_data
                    MERGE (cm:ClaimManagement {id: $management_id})
                    CREATE (u)-[:INSURANCE]->(a)
                    MERGE (cm)-[:LINKED_TO]->(a)
                    RETURN a, cm
                """
                result = neo4j.execute_query(query, parameters={
                    'application_data': application_data,
                    'email': email,
                    'management_id': management_id
                })
                if not result:
                    return jsonify({'error': 'Failed to update application or link nodes'}), 500

                return jsonify({
                    'message': 'Application updated and linked successfully',
                    'management_id': management_id
                }), 200

            except Exception as db_error:
                return jsonify({'error': f'Database operation failed: {str(db_error)}'}), 500

    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
