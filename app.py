import os
import boto3
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from PyPDF2 import PdfReader

app = Flask(__name__)
CORS(app, origins=["https://vercel-pdf-to-mp-3-delta.vercel.app"])

# Initialize the Polly client using environment variables
polly_client = boto3.client(
    'polly',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

# Ensure the 'temp' directory exists
temp_dir = "/tmp"

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
            temp_pdf_path = os.path.join(temp_dir, pdf_file.filename)
            pdf_file.save(temp_pdf_path)

            # Process PDF and convert to speech
            pdf_text = extract_text_from_pdf(temp_pdf_path)
            if not pdf_text.strip():
                return jsonify({"success": False, "message": "PDF extraction failed"}), 500

            audio_path = convert_text_to_speech_with_polly(pdf_text, pdf_file.filename)
            os.remove(temp_pdf_path)  # Clean up the PDF after processing

            # Send the audio file directly in the response
            return send_file(audio_path, as_attachment=True)

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
        print(f"PDF extraction error: {e}")  # Log the error
        raise RuntimeError("Error reading PDF: " + str(e))

def split_text(text, max_length=3000):
    """Split the text into chunks of max_length characters"""
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

def convert_text_to_speech_with_polly(text, filename):
    try:
        if not text.strip():
            raise ValueError("Cannot convert empty text to speech.")
        
        audio_files = []
        text_chunks = split_text(text)

        for i, chunk in enumerate(text_chunks):
            response = polly_client.synthesize_speech(
                Text=chunk,
                OutputFormat='mp3',
                VoiceId='Joanna'  # Customize the voice here as needed
            )

            # Create a temporary audio file for each chunk
            audio_path = os.path.join(temp_dir, f"{filename}_{i}.mp3")
            with open(audio_path, 'wb') as file:
                file.write(response['AudioStream'].read())

            audio_files.append(audio_path)

        # If you want to combine all audio chunks into one file, you can use pydub here
        # or you can return the first file or implement other ways to combine them.
        return audio_files[0]  # You could also combine and return a single file

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
