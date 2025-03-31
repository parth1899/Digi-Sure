from flask import Blueprint, request, jsonify
from utils.auth import token_required, get_user_from_token
from database.connection import Neo4jConnection
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from PIL import Image, ImageChops, ImageEnhance
import os
from config import Config

# Load your pre-trained model
model = load_model('routes/image_forgery_detection_casia2.h5')
image_size = (128, 128)

def convert_to_ela_image(path, quality=90):
    temp_filename = 'temp_file.jpg'
    image = Image.open(path).convert('RGB')
    image.save(temp_filename, 'JPEG', quality=quality)
    temp_image = Image.open(temp_filename)
    ela_image = ImageChops.difference(image, temp_image)
    extrema = ela_image.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    if max_diff == 0:
        max_diff = 1
    scale = 255.0 / max_diff
    ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)
    return ela_image

def prepare_image(image_path):
    ela_image = convert_to_ela_image(image_path)
    ela_image = ela_image.resize(image_size)
    ela_array = np.array(ela_image).astype('float32') / 255.0
    ela_array = np.expand_dims(ela_array, axis=0) 
    return ela_array

def predict_image(image_path):
    image = prepare_image(image_path)
    prediction = model.predict(image)
    predicted_class = np.argmax(prediction)
    class_labels = ['Fake', 'Real']
    return class_labels[predicted_class], float(np.max(prediction)), prediction.tolist()

# Create a blueprint for the forgery detection endpoints
forgery_bp = Blueprint('docs', __name__)

@forgery_bp.route('/upload', methods=['POST'])
@token_required
def detect_forgery(current_user_email):  # Now receives email instead of user object
    if 'file' not in request.files:
        return jsonify({'error': 'No file in the request.'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400
        
    # Save the file temporarily
    temp_path = os.path.join(Config.UPLOAD_FOLDER, file.filename)
    file.save(temp_path)
    
    try:
        predicted_label, confidence, full_confidence = predict_image(temp_path)
        
        neo4j = Neo4jConnection()
        # Modified query to match user by email
        query = """
        MATCH (u:User {email: $email})
        CREATE (d:Document {
            file_path: $file_path,
            file_name: $file_name,
            predicted_label: $predicted_label,
            confidence: $confidence,
            upload_date: datetime()
        })
        CREATE (u)-[:HAS_DOC]->(d)
        RETURN d
        """
        params = {
            'email': current_user_email,
            'file_path': temp_path,
            'file_name': file.filename,
            'predicted_label': predicted_label,
            'confidence': confidence
        }
        result = neo4j.execute_query(query, params)
        
        return jsonify({
            'predicted_label': predicted_label,
            'confidence': confidence,
            'full_confidence': full_confidence,
            'file_name': file.filename
        }), 200
        
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'error': str(e)}), 500

@forgery_bp.route('/get_images', methods=['GET'])
@token_required
def get_images(current_user_email):  # Now receives email instead of user object
    try:
        neo4j = Neo4jConnection()
        token = request.headers.get('Authorization').split(' ')[1]
        current_user_email = get_user_from_token(token)
        # Modified query to match user by email
        query = """
        MATCH (u:User {email: $email})-[:HAS_DOC]->(d:Document)
        RETURN d.file_name AS file_name,
               d.file_path AS file_path,
               d.predicted_label AS predicted_label,
               d.confidence AS confidence,
               d.upload_date AS upload_date
        ORDER BY d.upload_date DESC
        """
        params = {'email': current_user_email}
        result = neo4j.execute_query(query, params)
        
        images = [
            {
                'file_name': record['file_name'],
                'file_path': record['file_path'],
                'predicted_label': record['predicted_label'],
                'confidence': record['confidence'],
                'upload_date': record['upload_date'].isoformat() if record['upload_date'] else None
            }
            for record in result
        ]
        
        return jsonify({'images': images}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    