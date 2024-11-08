from flask import Flask, request, jsonify, url_for, render_template, send_file
from flask_cors import CORS 
from gtts import gTTS
from PyPDF2 import PdfReader
import pyttsx3
import os
import time
import tempfile
import boto3

# Initialize the Boto3 Polly client using environment variables
polly_client = boto3.client(
    'polly',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')  # Ensure to set the correct AWS region
)

app = Flask(__name__)
CORS(app, origins=["https://vercel-pdf-to-mp-3-delta.vercel.app"])


app = Flask(__name__)

# Ensure the 'temp' directory exists
temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
os.makedirs(temp_dir, exist_ok=True)

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
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf_file:
                temp_pdf_path = temp_pdf_file.name
                pdf_file.save(temp_pdf_path)

            # Process the file as before
            pdf_text = extract_text_from_pdf(temp_pdf_path)
            if not pdf_text.strip():
                return jsonify({"success": False, "message": "PDF extraction failed"}), 500

            audio_path = convert_text_to_speech(pdf_text, pdf_file.filename)
            os.remove(temp_pdf_path)  # Clean up the temporary file

            audio_url = url_for('download_file', filename=os.path.basename(audio_path))
            return jsonify({"success": True, "audio_url": audio_url})

        return jsonify({"success": False, "message": "Invalid file type"}), 400

    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({"success": False, "message": str(e)}), 500



def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"PDF extraction error: {e}")  # Log the error
        raise RuntimeError("Error reading PDF: " + str(e))

def convert_text_to_speech(text, filename):
    try:
        if not text.strip():
            raise ValueError("Cannot convert empty text to speech.")
        print(f"Converting text to speech for: {filename}")  # Log the filename
        
        engine = pyttsx3.init()
        audio_path = os.path.join(temp_dir, f"{filename}.mp3")
        engine.save_to_file(text, audio_path)
        engine.runAndWait()  # Wait for the speech to finish
        return audio_path
    except Exception as e:
        print(f"TTS conversion error: {e}")  # Log the error
        raise RuntimeError("Error converting text to speech: " + str(e))
    
    
@app.route('/download/<filename>')
def download_file(filename):
    audio_path = os.path.join(temp_dir, filename)
    if os.path.exists(audio_path):
        return send_file(audio_path, as_attachment=True)
    else:
        return jsonify({"success": False, "message": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=False)
