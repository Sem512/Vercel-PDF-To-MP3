import os
import json
import boto3
from flask import Flask, request, jsonify, render_template
from PyPDF2 import PdfReader

app = Flask(__name__)
api_gateway_url = 'https://ccvjmdt3th.execute-api.eu-north-1.amazonaws.com/prod/convert-pdf'  # Lambda API URL

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    try:
        # Check if a file was uploaded
        if 'pdf' not in request.files:
            return jsonify({"success": False, "message": "No file part"}), 400
        
        pdf_file = request.files['pdf']
        if pdf_file.filename == '':
            return jsonify({"success": False, "message": "No selected file"}), 400

        # Save and extract text from the PDF
        temp_pdf_path = os.path.join('/tmp', pdf_file.filename)
        pdf_file.save(temp_pdf_path)
        pdf_text = extract_text_from_pdf(temp_pdf_path)

        if not pdf_text.strip():
            return jsonify({"success": False, "message": "PDF extraction failed"}), 500

        # Send extracted text to Lambda
        response = trigger_lambda(pdf_text, pdf_file.filename)
        
        # Return Lambda’s response (audio URL)
        if response.get('statusCode') == 200:
            return jsonify({"success": True, "audio_url": response.get('body')}), 200
        else:
            return jsonify({"success": False, "message": "Error in Lambda processing"}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = "".join(page.extract_text() or "" for page in reader.pages)
        return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        raise RuntimeError("Error reading PDF: " + str(e))

def trigger_lambda(text, filename):
    payload = {'text': text, 'filename': filename}
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(api_gateway_url, json=payload, headers=headers)
    return response.json()

if __name__ == '__main__':
    app.run(debug=True)
