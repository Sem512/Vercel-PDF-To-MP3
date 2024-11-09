import os
import json
import boto3
from flask import Flask, request, jsonify, render_template
from PyPDF2 import PdfReader

app = Flask(__name__)

# Initialize the API Gateway client
api_gateway_url = 'https://ccvjmdt3th.execute-api.eu-north-1.amazonaws.com/prod'  # Replace with your API Gateway endpoint

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

            # Debug log: Check the extracted text
            print(f"Extracted Text: {pdf_text}")  # Log the full extracted text

            if not pdf_text.strip():
                return jsonify({"success": False, "message": "PDF extraction failed"}), 500

            # Trigger AWS Lambda for text-to-speech conversion
            response = trigger_lambda(pdf_text, pdf_file.filename)

            # Return the audio file URL(s)
            if response.get('statusCode') == 200:
                return jsonify({"success": True, "audio_files": response.get('body')}), 200

            return jsonify({"success": False, "message": "Error in Lambda processing"}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text() or ""
            # Clean the extracted text (remove unwanted characters, handle encoding issues)
            page_text = page_text.replace('\n', ' ').strip()  # Clean line breaks
            text += page_text
        return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        raise RuntimeError("Error reading PDF: " + str(e))


def trigger_lambda(text, filename):
    # Send request to Lambda (API Gateway endpoint)
    payload = {
        'text': text,
        'filename': filename
    }

    response = boto3.client('apigateway').test_invoke_method(
        restApiId='ccvjmdt3th',  # Replace with your API ID
        resourceId='/convert-pdf',  # Replace with your resource ID
        httpMethod='POST',
        body=json.dumps(payload)
    )

    return json.loads(response['body'])

if __name__ == '__main__':
    app.run(debug=True)
