import os
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from utils.auth import token_required
from database.connection import Neo4jConnection
from config import Config
import openbharatocr
from pdf2image import convert_from_path

document_bp = Blueprint('document', __name__)

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def process_aadhaar_details(aadhar_info_front, aadhar_info_back):
    """Process and validate Aadhaar card details from both front and back"""
    # Validate Aadhaar number
    aadhar_number = aadhar_info_front['Aadhaar Number'].replace(' ', '')
    if not aadhar_number.isdigit() or len(aadhar_number) != 12:
        raise ValueError("Invalid Aadhaar number format")

    # Process date
    try:
        dob = datetime.strptime(aadhar_info_front['Date/Year of Birth'], '%d/%m/%Y')
        formatted_dob = dob.strftime('%Y-%m-%d')
    except ValueError:
        try:
            dob = datetime.strptime(aadhar_info_front['Date/Year of Birth'], '%Y')
            formatted_dob = f"{dob.year}-01-01"
        except ValueError:
            raise ValueError("Invalid date format in Date/Year of Birth")

    # Process gender
    valid_genders = {'M', 'F', 'MALE', 'FEMALE', 'OTHER'}
    if aadhar_info_front['Gender'].upper() not in valid_genders:
        raise ValueError("Invalid gender value")

    normalized_gender = ('MALE' if aadhar_info_front['Gender'].upper() in {'M', 'MALE'}
                        else 'FEMALE' if aadhar_info_front['Gender'].upper() in {'F', 'FEMALE'}
                        else 'OTHER')

    # Validate address
    if 'Address' not in aadhar_info_back or not aadhar_info_back['Address'].strip():
        raise ValueError("Missing or invalid address information")

    # Validate father's name
    if 'Father Name' not in aadhar_info_back or not aadhar_info_back['Father Name'].strip():
        raise ValueError("Missing or invalid father's name")

    return formatted_dob, normalized_gender, aadhar_number, aadhar_info_back['Address'].strip(), aadhar_info_back['Father Name'].strip()

@document_bp.route('/upload-aadhaar-card', methods=['POST'])
@token_required
def upload_aadhar_card(current_user):
    """Upload and process Aadhaar card with name matching and validation"""
    try:
        if 'file' not in request.files:
            return jsonify({'message': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'message': 'File type not allowed. Please upload PNG, JPG, JPEG, or PDF files only'}), 400

        # Save and process file
        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)

        try:
            # Handle PDF conversion if needed
            if filename.lower().endswith('.pdf'):
                images = convert_from_path(file_path)
                if not images:
                    raise ValueError("Failed to convert PDF to image")
                temp_image_path = os.path.join(Config.UPLOAD_FOLDER, f"{os.path.splitext(filename)[0]}.jpg")
                images[0].save(temp_image_path, 'JPEG')
                os.remove(file_path)
                file_path = temp_image_path

            # Extract Aadhar details from both sides
            aadhar_info_front = openbharatocr.front_aadhaar(file_path)
            aadhar_info_back = openbharatocr.back_aadhaar(file_path)
            
            if not all(key in aadhar_info_front for key in ['Full Name', 'Date/Year of Birth', 'Gender', 'Aadhaar Number']):
                raise ValueError("Missing required Aadhaar information from front side")

            if not all(key in aadhar_info_back for key in ['Father Name', 'Address']):
                raise ValueError("Missing required Aadhaar information from back side")

            # Process name
            aadhar_name_parts = aadhar_info_front['Full Name'].strip().split()
            if len(aadhar_name_parts) < 2:
                raise ValueError("Invalid name format in Aadhaar card")

            aadhar_surname = aadhar_name_parts[0]
            aadhar_name = aadhar_name_parts[1]
            aadhar_middle_name = " ".join(aadhar_name_parts[2:]) if len(aadhar_name_parts) > 2 else ""

            # Validate name match
            def normalize_name(name):
                return " ".join(name.lower().split())

            if (normalize_name(current_user.surname) != normalize_name(aadhar_surname) or
                normalize_name(current_user.name) != normalize_name(aadhar_name)):
                return jsonify({
                    'message': 'Name mismatch',
                    'error': 'The name on the Aadhaar card does not match your registered name'
                }), 400

            # Process all details
            formatted_dob, normalized_gender, aadhar_number, address, father_name = process_aadhaar_details(
                aadhar_info_front, aadhar_info_back
            )

            # Update database with additional information
            db = Neo4jConnection()
            with db.get_session() as session:
                result = session.run(
                    """
                    MATCH (u:User {email: $email, name: $name, surname: $surname})
                    MERGE (i:UserInfo {aadhar_number: $aadhar_number})
                    ON CREATE SET 
                        i.name = $full_name,
                        i.surname = $surname,
                        i.given_name = $name,
                        i.middle_name = $middle_name,
                        i.father_name = $father_name,
                        i.address = $address,
                        i.dob = $dob,
                        i.gender = $gender,
                        i.created_at = datetime()
                    ON MATCH SET 
                        i.name = $full_name,
                        i.surname = $surname,
                        i.given_name = $name,
                        i.middle_name = $middle_name,
                        i.father_name = $father_name,
                        i.address = $address,
                        i.dob = $dob,
                        i.gender = $gender,
                        i.updated_at = datetime()
                    MERGE (u)-[:HAS_VERIFIED_AADHAAR]->(i)
                    RETURN i
                    """,
                    email=current_user.email,
                    name=current_user.name,
                    surname=current_user.surname,
                    full_name=aadhar_info_front['Full Name'].strip(),
                    middle_name=aadhar_middle_name,
                    father_name=father_name,
                    address=address,
                    aadhar_number=aadhar_number,
                    dob=formatted_dob,
                    gender=normalized_gender
                )
                
                if not result.single():
                    raise Exception("Failed to update database with Aadhaar information")

            return jsonify({
                'message': 'Aadhaar card processed successfully',
                'data': {
                    'name': aadhar_info_front['Full Name'].strip(),
                    'dob': formatted_dob,
                    'gender': normalized_gender,
                    'aadhaar_number': aadhar_number,
                    'father_name': father_name,
                    'address': address
                }
            }), 200

        except ValueError as ve:
            return jsonify({'message': 'Validation error', 'error': str(ve)}), 422
        except Exception as e:
            return jsonify({'message': 'Error processing Aadhaar card', 'error': str(e)}), 500
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
    
    except Exception as e:
        return jsonify({'message': 'Internal Server Error', 'error': str(e)}), 500