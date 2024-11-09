import os
import json
import requests
from PyPDF2 import PdfReader
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Lambda URL for POST request
lambda_url = "https://ccvjmdt3th.execute-api.eu-north-1.amazonaws.com/prod/convert-pdf"

def extract_text_from_pdf(pdf_path):
    """Extract text from the PDF file"""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    """Handle the PDF upload and trigger Lambda for conversion"""
    if 'pdf' not in request.files:
        return jsonify({"error": "No file part"}), 400

    pdf_file = request.files['pdf']
    if pdf_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if pdf_file and pdf_file.filename.endswith('.pdf'):
        # Save the PDF to a temporary location
        temp_pdf_path = os.path.join('/tmp', pdf_file.filename)
        pdf_file.save(temp_pdf_path)

        # Extract text from the PDF
        pdf_text = extract_text_from_pdf(temp_pdf_path)
        if not pdf_text.strip():
            return jsonify({"error": "No text extracted from PDF"}), 500


        logger.info(pdf_text)
        
        # Send the extracted text to Lambda
        payload = {
            'text': pdf_text,
            'filename': pdf_file.filename
        }

        headers = {
            'Content-Type': 'application/json'
        }

        # Call the Lambda function with extracted text
        try:
            response = requests.post(lambda_url, json=payload, headers=headers)
            response_data = response.json()

            if response.status_code == 200:
                return jsonify({
                    'success': True,
                    'audio_url': response_data['audio_url']
                }), 200
            else:
                return jsonify({
                    'error': 'Error during Lambda processing',
                    'message': response_data.get('message', '')
                }), 500
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f"Error calling Lambda: {str(e)}"}), 500

    return jsonify({"error": "Invalid file type"}), 400

if __name__ == '__main__':
    app.run(debug=True)
