# routes/document_extract.py
from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
import base64
from mistralai import Mistral
from routes.helper.structured_response import DocumentProcessor
from config import Config
from io import BytesIO

document_extract_bp = Blueprint('document_extract', __name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS    

@document_extract_bp.route('/extract_policy', methods=['POST'])
def policy_extraction():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(file_path)
    
    try:
        api_key = Config.MISTRAL_API_KEY
        if not api_key:
            raise ValueError("MISTRAL_API_KEY is not configured in application settings")
        
        client = Mistral(api_key=api_key)
        extracted_text = ""

        
        # Process PDF file
        with open(file_path, 'rb') as pdf_file:
            uploaded_file = client.files.upload(
                file={
                    "file_name": filename,
                    "content": pdf_file,
                },
                purpose="ocr"
            )
        
        signed_url = client.files.get_signed_url(file_id=uploaded_file.id)
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": signed_url.url,
            }
        )
        # Extract text from PDF pages
        extracted_text = "\n\n".join(page.markdown for page in ocr_response.pages)
            

        # Process extracted text
        processor = DocumentProcessor()
        structured_data = processor.process_insurance_extraction(extracted_text)
        
        # os.remove(file_path)
        return jsonify(structured_data.model_dump())
    
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        current_app.logger.error(f"OCR processing failed: {str(e)}")
        return jsonify({"error": str(e)}), 500
    

@document_extract_bp.route('/extract_claim', methods=['POST'])
def claim_extraction():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(file_path)
    
    try:
        api_key = Config.MISTRAL_API_KEY
        if not api_key:
            raise ValueError("MISTRAL_API_KEY is not configured in application settings")
        
        client = Mistral(api_key=api_key)
        extracted_text = ""

        
        # Process PDF file
        with open(file_path, 'rb') as pdf_file:
            uploaded_file = client.files.upload(
                file={
                    "file_name": filename,
                    "content": pdf_file,
                },
                purpose="ocr"
            )
        
        signed_url = client.files.get_signed_url(file_id=uploaded_file.id)
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": signed_url.url,
            }
        )
        # Extract text from PDF pages
        extracted_text = "\n\n".join(page.markdown for page in ocr_response.pages)
            

        # Process extracted text
        processor = DocumentProcessor()
        structured_data = processor.process_claim_extraction(extracted_text)
        
        # os.remove(file_path)
        return jsonify(structured_data.model_dump())
    
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        current_app.logger.error(f"OCR processing failed: {str(e)}")
        return jsonify({"error": str(e)}), 500