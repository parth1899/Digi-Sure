from flask import Blueprint, jsonify, request
import pandas as pd
import os
import uuid
from database.connection import Neo4jConnection
from utils.auth import token_required

# Initialize Blueprint
profile_bp = Blueprint('profile', __name__)
neo4j = Neo4jConnection()

# Helper function to convert Neo4j node to dictionary
def dict_from_node(node):
    if node is None:
        return {}
    return dict(node)

# Generate unique customer ID
def generate_customer_id():
    # Format: CUS-XXXX-XXXX-XXXX
    unique_id = str(uuid.uuid4()).upper().replace('-', '')
    return f"CUS-{unique_id[:4]}-{unique_id[4:8]}-{unique_id[8:12]}"

@profile_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user_email):
    """Get complete user profile including banking and insurance details"""
    try:
        with neo4j.get_session() as session:
            # First check if customerId exists, generate if not
            check_result = session.run("""
                MATCH (u:User {email: $email})
                RETURN u
            """, email=current_user_email)
            
            user_record = check_result.single()
            if not user_record:
                return jsonify({'message': 'User not found'}), 404

            user_data = dict_from_node(user_record['u'])
            
            # Generate and update customerId if empty
            if not user_data.get('customerId'):
                new_customer_id = generate_customer_id()
                update_result = session.run("""
                    MATCH (u:User {email: $email})
                    SET u.customerId = $customerId
                    RETURN u
                """, email=current_user_email, customerId=new_customer_id)
                
                user_data = dict_from_node(update_result.single()['u'])
            
            # Now fetch complete profile data
            result = session.run("""
                MATCH (u:User {email: $email})
                OPTIONAL MATCH (u)-[:HAS_BANKING_DETAILS]->(b:BankingDetails)
                OPTIONAL MATCH (u)-[:HAS_APPLICATION]->(a:Application)
                WHERE a.status = 'ACTIVE' AND a.type = 'INSURANCE'
                RETURN u, b, collect(a) as insurances
            """, email=current_user_email)
            
            record = result.single()
            
            user_data = dict_from_node(record['u'])
            banking_data = dict_from_node(record['b'])
            insurances = [dict_from_node(insurance) for insurance in record['insurances']]
            other_details = dict_from_node(record['d']) if record.get('d') else {}

            # Mask sensitive data
            if banking_data:
                if banking_data.get('aadharNumber'):
                    banking_data['aadharNumber'] = f"XXXX XXXX {banking_data['aadharNumber'][-4:]}"
                if banking_data.get('panNumber'):
                    banking_data['panNumber'] = f"XXXXX{banking_data['panNumber'][-5:]}"
                if banking_data.get('accountNumber'):
                    banking_data['accountNumber'] = f"XXXX XXXX {banking_data['accountNumber'][-4:]}"

            response = {
                'name': user_data.get('name'),
                'email': user_data.get('email'),
                'mobile': user_data.get('mobile'),
                'customerId': user_data.get('customerId'),
                'address': user_data.get('address', ''),
                'profilePicture': user_data.get('profilePicture', ''),
                **banking_data,
                'insurancePolicies': insurances,
                'otherDetails': other_details
            }

            return jsonify(response)

    except Exception as e:
        print(f"Error in get_profile: {str(e)}")
        return jsonify({'message': f'Error fetching profile: {str(e)}'}), 500

@profile_bp.route('/profile/personal', methods=['PUT'])
@token_required
def update_personal_info(current_user_email):
    """Update personal information"""
    try:
        data = request.json
        with neo4j.get_session() as session:
            result = session.run("""
                MATCH (u:User {email: $email})
                SET u.name = $name,
                    u.phone = $phone
                RETURN u
            """, email=current_user_email, name=data.get('name'), phone=data.get('phone'))
            
            updated_user = dict_from_node(result.single()['u'])
            return jsonify({
                'message': 'Personal information updated successfully',
                'data': updated_user
            })

    except Exception as e:
        print(f"Error in update_personal_info: {str(e)}")
        return jsonify({'message': f'Error updating personal info: {str(e)}'}), 500

@profile_bp.route('/profile/banking', methods=['PUT'])
@token_required
def update_banking_details(current_user_email):
    """Update or create banking details after comprehensive validation against CSV"""
    try:
        data = request.json
        aadhar_number = data.get('aadharNumber')
        pan_number = data.get('panNumber')
        
        # First get user details from database
        with neo4j.get_session() as session:
            user_result = session.run("""
                MATCH (u:User {email: $email})
                RETURN u
            """, email=current_user_email)
            
            user_record = user_result.single()
            if not user_record:
                return jsonify({'message': 'User not found'}), 404
                
        # Proceed with update only if validation passed
        with neo4j.get_session() as session:
            result = session.run("""
                MATCH (u:User {email: $email})
                MERGE (u)-[:HAS_BANKING_DETAILS]->(b:BankingDetails)
                SET b.aadharNumber = $aadhar,
                    b.panNumber = $pan,
                    b.accountNumber = $account,
                    b.ifscCode = $ifsc
                RETURN b
            """, 
                email=current_user_email,
                aadhar=aadhar_number,
                pan=pan_number,
                account=data.get('accountNumber'),
                ifsc=data.get('ifscCode')
            )
            
            updated_banking = dict_from_node(result.single()['b'])
            return jsonify({
                'message': 'Banking details updated successfully',
                'data': updated_banking
            })

    except Exception as e:
        print(f"Error in update_banking_details: {str(e)}")
        return jsonify({'message': f'Error updating banking details: {str(e)}'}), 500

@profile_bp.route('/profile/address', methods=['PUT'])
@token_required
def update_address(current_user_email):
    """Update address information"""
    try:
        data = request.json
        with neo4j.get_session() as session:
            result = session.run("""
                MATCH (u:User {email: $email})
                SET u.address = $address
                RETURN u
            """, email=current_user_email, address=data.get('address'))
            
            updated_user = dict_from_node(result.single()['u'])
            return jsonify({
                'message': 'Address updated successfully',
                'data': updated_user
            })

    except Exception as e:
        print(f"Error in update_address: {str(e)}")
        return jsonify({'message': f'Error updating address: {str(e)}'}), 500

@profile_bp.route('/profile/insurance', methods=['GET'])
@token_required
def get_insurance_policies(current_user_email):
    """Get active insurance policies"""
    try:
        with neo4j.get_session() as session:
            result = session.run("""
                MATCH (u:User {email: $email})-[:HAS_APPLICATION]->(a:Application)
                WHERE a.status = 'ACTIVE' AND a.type = 'INSURANCE'
                RETURN a
            """, email=current_user_email)
            
            policies = [dict_from_node(record['a']) for record in result]
            return jsonify(policies)

    except Exception as e:
        print(f"Error in get_insurance_policies: {str(e)}")
        return jsonify({'message': f'Error fetching insurance policies: {str(e)}'}), 500
    
@profile_bp.route('/profile/other-details', methods=['PUT'])
@token_required
def update_other_details(current_user_email):
    """Update or create other details for the user."""
    try:
        data = request.json
        with neo4j.get_session() as session:
            session.run("""
                MATCH (u:User {email: $email})
                MERGE (u)-[:HAS_DETAILS]->(d:OtherDetails)
                SET d.sex = $sex,
                    d.dob = $dob,
                    d.education_level = $education_level,
                    d.occupation = $occupation,
                    d.hobbies = $hobbies,
                    d.relationship = $relationship
                RETURN d
            """, 
                email=current_user_email,
                sex=data.get('sex'),
                dob=data.get('dob'),
                education_level=data.get('education_level'),
                occupation=data.get('occupation'),
                hobbies=data.get('hobbies'),
                relationship=data.get('relationship')
            )
            
            return jsonify({
                'message': 'Other details updated successfully'
            })

    except Exception as e:
        print(f"Error in update_other_details: {str(e)}")
        return jsonify({'message': f'Error updating other details: {str(e)}'}), 500