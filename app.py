import os
import json
import logging
from flask import Flask, request, jsonify, render_template
import boto3
from PyPDF2 import PdfReader
import tempfile
from io import BytesIO

# Initialize Flask app
app = Flask(__name__)

# Initialize AWS clients
lambda_client = boto3.client('lambda', region_name='us-east-1')  # Adjust region if necessary

# Set up logging
logging.basicConfig(level=logging.INFO)

# Route to serve the index.html page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle PDF file upload and invoke Lambda function
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400

    file = request.files['pdf']
    
    if file.filename == '':
        return jsonify({"success": False, "message": "No selected file"}), 400

    try:
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(file)
        
        # Send the extracted text to the Lambda function
        lambda_response = invoke_lambda(extracted_text, file.filename)
        
        # Get the audio URL returned from Lambda
        audio_url = lambda_response.get('audio_url')

        return jsonify({
            "success": True, 
            "audio_url": audio_url,
            "extracted_text": extracted_text  # Return the extracted text for further processing
        })

    except Exception as e:
        logging.error(f"Error during file upload and processing: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

def extract_text_from_pdf(pdf_file):
    """ Extract text from a PDF file """
    try:
        # Create a temporary file to store the uploaded PDF content
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(pdf_file.read())
            tmp_file.close()
            
            # Read the PDF file
            reader = PdfReader(tmp_file.name)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
        
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def invoke_lambda(text, filename):
    """ Invoke Lambda function to convert text to MP3 and return the audio URL """
    try:
        # Prepare the payload to send to Lambda
        payload = {
            "text": text,
            "filename": filename
        }

        # Invoke the Lambda function
        response = lambda_client.invoke(
            FunctionName='https://ccvjmdt3th.execute-api.eu-north-1.amazonaws.com/prod/convert-pdf',  # Replace with your actual Lambda function name
            InvocationType='RequestResponse',  # This will wait for the response
            Payload=json.dumps(payload)
        )

        # Read the Lambda response
        response_payload = json.loads(response['Payload'].read().decode('utf-8'))

        if 'audio_url' in response_payload:
            return response_payload
        else:
            raise Exception("Lambda did not return a valid audio URL.")
    except Exception as e:
        raise Exception(f"Error invoking Lambda function: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
