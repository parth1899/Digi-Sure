import os
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from utils.auth import token_required, get_user_from_token
from database.connection import Neo4jConnection 
from config import Config

document_bp = Blueprint('document', __name__)

def check_existing_aadhaar(email, db_session):
    """Check if user already has an Aadhaar card uploaded"""
    result = db_session.run(
        """
        MATCH (user:User {email: $email})-[:HAS_AADHAAR_CARD]->(file:File)
        RETURN file.path as file_path
        """,
        email=email
    )
    return result.single() is not None
@document_bp.route('/upload-aadhaar-card', methods=['POST'])
@token_required
def upload_aadhar_card(current_user):
    try:
        # Get the authorization token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Missing or invalid authorization token'}), 401
        
        token = auth_header.split(' ')[1]
        email = get_user_from_token(token)
        
        if not email:
            return jsonify({'message': 'Invalid token or user not found'}), 401

        # Check if the 'file' part is in the request
        if 'file' not in request.files:
            return jsonify({'message': 'No file part'}), 400
        
        file = request.files['file']
        
        # Check if the file has no name
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        
        # Validate the file type
        if not allowed_file(file.filename):
            return jsonify({'message': 'Invalid file format'}), 400

        # Create a unique filename using email and timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f"aadhaar_{email}_{timestamp}.{original_extension}"
        filename = secure_filename(filename)

        # Ensure upload directory exists
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Database operations
        db = Neo4jConnection()
        with db.get_session() as session:
            if check_existing_aadhaar(email, session):
                return jsonify({
                    'message': 'Aadhaar card already exists for this user. Please delete the existing one before uploading a new card.'
                }), 409  # 409 Conflict status code
            result = session.run(
                """
                MATCH (user:User {email: $email})
                MERGE (file:File {path: $file_path})
                ON CREATE SET file.uploaded_at = $timestamp
                MERGE (user)-[r:HAS_AADHAAR_CARD]->(file)
                RETURN user.email as user_email, file.path as file_path
                """,
                email=email,
                file_path=file_path,
                timestamp=datetime.now().isoformat()
            )
            
            record = result.single()
            if not record:
                os.remove(file_path)
                return jsonify({'message': 'Failed to create relationship in database'}), 500
            
            return jsonify({
                'message': 'Aadhaar card uploaded successfully',
                'file_path': file_path,
                'email': email
            })
            
    except Exception as e:
        # Clean up the uploaded file if any operation fails
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'message': f'Error processing request: {str(e)}'}), 500

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS