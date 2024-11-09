import os
import json
import boto3
import requests
from flask import Flask, request, jsonify, render_template
from PyPDF2 import PdfReader

app = Flask(__name__)

# API Gateway URL (Lambda function endpoint via API Gateway)
api_gateway_url = 'https://ccvjmdt3th.execute-api.eu-north-1.amazonaws.com/prod/convert-pdf'  # Replace with your API Gateway endpoint

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
            lambda_response = trigger_lambda(pdf_text, pdf_file.filename)

            # Check if the response from Lambda is successful
            if lambda_response.get('statusCode') == 200:
                audio_files = json.loads(lambda_response['body']).get('audio_url')
                return jsonify({"success": True, "audio_files": audio_files}), 200

            return jsonify({"success": False, "message": "Error in Lambda processing"}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


def extract_text_from_pdf(pdf_path):
    """Extracts text from the given PDF file using PyPDF2"""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        raise RuntimeError("Error reading PDF: " + str(e))


def trigger_lambda(text, filename):
    """Triggers the Lambda function via API Gateway"""
    payload = {
        'text': text,
        'filename': filename
    }

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        # Send request to API Gateway (Lambda function)
        response = requests.post(api_gateway_url, json=payload, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()  # Return the response from Lambda as a JSON object
        else:
            print(f"Error from Lambda: {response.text}")
            return {'statusCode': 500, 'body': json.dumps({'message': 'Lambda error'})}

    except Exception as e:
        print(f"Error triggering Lambda: {e}")
        return {'statusCode': 500, 'body': json.dumps({'message': str(e)})}


if __name__ == '__main__':
    app.run(debug=True)
