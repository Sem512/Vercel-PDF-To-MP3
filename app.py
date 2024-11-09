from flask import Flask, request, jsonify, url_for, render_template, send_file, make_response
from flask_cors import CORS
import os
import boto3
from PyPDF2 import PdfReader

app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable CORS globally with credentials support

# Set up the Polly client and /tmp directory for file storage
polly_client = boto3.client(
    'polly',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)
temp_dir = "/tmp"

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_pdf():
    if request.method == 'OPTIONS':
        # Send CORS headers for the preflight request
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = 'https://https://vercel-pdf-to-mp-3-delta.vercel.app'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    try:
        if 'pdf' not in request.files:
            return jsonify({"success": False, "message": "No file part"}), 400

        pdf_file = request.files['pdf']
        if pdf_file.filename == '':
            return jsonify({"success": False, "message": "No selected file"}), 400

        if pdf_file and pdf_file.filename.endswith('.pdf'):
            temp_pdf_path = os.path.join(temp_dir, pdf_file.filename)
            pdf_file.save(temp_pdf_path)

            # Process PDF and convert to speech
            pdf_text = extract_text_from_pdf(temp_pdf_path)
            if not pdf_text.strip():
                return jsonify({"success": False, "message": "PDF extraction failed"}), 500

            audio_path = convert_text_to_speech_with_polly(pdf_text, pdf_file.filename)
            os.remove(temp_pdf_path)  # Clean up PDF after processing

            # Send the audio file directly
            response = make_response(send_file(audio_path, as_attachment=True))
            response.headers['Access-Control-Allow-Origin'] = 'https://vercel-pdf-to-mp-3-delta.vercel.app'
            return response

        return jsonify({"success": False, "message": "Invalid file type"}), 400

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        raise RuntimeError("Error reading PDF: " + str(e))

def convert_text_to_speech_with_polly(text, filename):
    try:
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Joanna'
        )
        audio_path = os.path.join(temp_dir, f"{filename}.mp3")
        with open(audio_path, 'wb') as audio_file:
            audio_file.write(response['AudioStream'].read())
        return audio_path
    except Exception as e:
        print(f"TTS conversion error: {e}")
        raise RuntimeError("Error converting text to speech: " + str(e))

@app.route('/download/<filename>')
def download_file(filename):
    audio_path = os.path.join(temp_dir, filename)
    if os.path.exists(audio_path):
        response = make_response(send_file(audio_path, as_attachment=True))
        response.headers['Access-Control-Allow-Origin'] = 'https://vercel-pdf-to-mp-3-delta.vercel.app'
        return response
    else:
        return jsonify({"success": False, "message": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=False)
