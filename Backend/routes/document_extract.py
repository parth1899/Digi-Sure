# routes/document_extract.py
from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
from routes.helper.structured_response import DocumentProcessor

document_extract_bp = Blueprint('document_extract', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_image(image_path):
    """Extract text from image file using Tesseract OCR"""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        raise e

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file by converting pages to images"""
    text = ""
    try:
        pdf_document = fitz.open(pdf_path)
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"temp_page_{page_num}.png")
            pix.save(img_path)
            text += extract_text_from_image(img_path) + "\n"
            os.remove(img_path)  # Clean up temporary image
        pdf_document.close()
        return text
    except Exception as e:
        raise e

@document_extract_bp.route('/ocr', methods=['POST'])
def ocr_extraction():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            if filename.lower().endswith('.pdf'):
                extracted_text = extract_text_from_pdf(file_path)
            else:
                extracted_text = extract_text_from_image(file_path)

            processor = DocumentProcessor()
            structured_data = processor.process_extraction(extracted_text)
            
            os.remove(file_path)  # Clean up uploaded file
            # return jsonify({"text": extracted_text})
            return jsonify(structured_data.model_dump())
        
        except Exception as e:
            os.remove(file_path)
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "Invalid file type"}), 400