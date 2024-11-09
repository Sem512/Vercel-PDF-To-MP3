import os
import boto3
import json
import requests
from flask import Flask, request, jsonify, render_template
from PyPDF2 import PdfReader

app = Flask(__name__)

# Initialize the API Gateway URL for Lambda
api_gateway_url = 'https://ccvjmdt3th.execute-api.eu-north-1.amazonaws.com/prod/convert-pdf'  # Replace with your API Gateway URL

# Initialize the S3 client (optional, if you need to handle file uploads in S3 directly)
s3_client = boto3.client('s3')
BUCKET_NAME = 'audio-bucket-pdf-to-mp3'  # Replace with your S3 bucket name

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    try:
        # Check if the file is part of the request
        if 'pdf' not in request.files:
            return jsonify({"success": False, "message": "No file part"}), 400

        pdf_file = request.files['pdf']
        
        # Check if the file is empty
        if pdf_file.filename == '':
            return jsonify({"success": False, "message": "No selected file"}), 400
        
        # Check if the file is a PDF
        if pdf_file and pdf_file.filename.endswith('.pdf'):
            # Save the file temporarily
            temp_pdf_path = os.path.join('/tmp', pdf_file.filename)
            pdf_file.save(temp_pdf_path)

            # Process PDF to extract text
            pdf_text = extract_text_from_pdf(temp_pdf_path)
            if not pdf_text.strip():
                return jsonify({"success": False, "message": "PDF extraction failed"}), 500

            # Trigger AWS Lambda for text-to-speech conversion
            response = trigger_lambda(pdf_text, pdf_file.filename)

            # Return the audio file URL(s)
            if response.get('statusCode') == 200:
                return jsonify({"success": True, "audio_files": response.get('audio_url')}), 200

            return jsonify({"success": False, "message": "Error in Lambda processing"}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        print(text)
        return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        raise RuntimeError("Error reading PDF: " + str(e))

def trigger_lambda(text, filename):
    # Send the extracted text to Lambda via API Gateway
    payload = {
        'text': text,
        'filename': filename
    }

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        # Make a POST request to the API Gateway endpoint
        response = requests.post(api_gateway_url, data=json.dumps(payload), headers=headers)

        if response.status_code == 200:
            return response.json()  # This should contain the audio URL
        else:
            raise Exception(f"Lambda error: {response.text}")
    
    except Exception as e:
        print(f"Error triggering Lambda: {e}")
        raise

if __name__ == '__main__':
    app.run(debug=True)
