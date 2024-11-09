import os
import boto3
import json
from flask import Flask, request, jsonify, render_template
from PyPDF2 import PdfReader

app = Flask(__name__)
# Initialize the Lambda client
lambda_client = boto3.client('lambda', region_name='eu-north-1')  # Make sure to set your region

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    try:
        if 'pdf' not in request.files:
            return jsonify({"success": False, "message": "No file part"}), 400

        pdf_file = request.files['pdf']
        if pdf_file.filename == '':
            return jsonify({"success": False, "message": "No selected file"}), 400

        if pdf_file and pdf_file.filename.endswith('.pdf'):
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
                body = json.loads(response.get('body'))
                return jsonify({"success": True, "audio_files": body.get('audio_files', [])})

            return jsonify({"success": False, "message": "Error in Lambda processing"}), 500

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        raise RuntimeError("Error reading PDF: " + str(e))

def trigger_lambda(text, filename):
    payload = {
        'text': text,
        'filename': filename
    }

    # Ensure the API Gateway URL is correct here
    api_gateway_url = 'https://ccvjmdt3th.execute-api.eu-north-1.amazonaws.com/prod/convert-pdf'  # Replace with your API Gateway endpoint

    # Use requests module to call the API Gateway endpoint
    import requests
    response = requests.post(api_gateway_url, json=payload)

    if response.status_code == 200:
        return response.json()  # Assuming the response is in JSON format
    else:
        raise Exception(f"Error calling Lambda: {response.text}")

if __name__ == '__main__':
    app.run(debug=False)
