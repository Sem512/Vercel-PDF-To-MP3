from flask import Flask, request, jsonify, url_for, render_template, send_file
from flask_cors import CORS
import boto3
from PyPDF2 import PdfReader
import os

app = Flask(__name__)
CORS(app, origins=["https://vercel-pdf-to-mp-3-delta.vercel.app"])

# Ensure the 'temp' directory exists for temporary storage of files
temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
os.makedirs(temp_dir, exist_ok=True)

# Initialize the Amazon Polly client using environment variables
polly_client = boto3.client(
    'polly',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    try:
        # Check if the request contains a PDF file
        if 'pdf' not in request.files:
            return jsonify({"success": False, "message": "No file part"}), 400

        pdf_file = request.files['pdf']
        if pdf_file.filename == '':
            return jsonify({"success": False, "message": "No selected file"}), 400

        # Save the PDF temporarily
        if pdf_file and pdf_file.filename.endswith('.pdf'):
            temp_pdf_path = os.path.join(temp_dir, pdf_file.filename)
            pdf_file.save(temp_pdf_path)

            # Extract text from the PDF
            pdf_text = extract_text_from_pdf(temp_pdf_path)
            if not pdf_text.strip():
                return jsonify({"success": False, "message": "PDF extraction failed"}), 500

            # Convert the extracted text to speech using Amazon Polly
            audio_path = convert_text_to_speech(pdf_text, pdf_file.filename)
            os.remove(temp_pdf_path)  # Clean up the PDF file after conversion

            # Send back the audio file URL
            audio_url = url_for('download_file', filename=os.path.basename(audio_path))
            return jsonify({"success": True, "audio_url": audio_url})

        return jsonify({"success": False, "message": "Invalid file type"}), 400

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

def extract_text_from_pdf(pdf_path):
    """Extracts text from each page of a PDF."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        raise RuntimeError("Error reading PDF: " + str(e))

def convert_text_to_speech(text, filename):
    """Converts text to speech using Amazon Polly."""
    try:
        # Request speech synthesis from Polly
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId="Joanna"  # Choose an Amazon Polly voice (you can change this)
        )
        
        # Save the audio file
        audio_path = os.path.join(temp_dir, f"{filename}.mp3")
        with open(audio_path, 'wb') as audio_file:
            audio_file.write(response['AudioStream'].read())
        
        return audio_path
    except Exception as e:
        print(f"TTS conversion error: {e}")
        raise RuntimeError("Error converting text to speech: " + str(e))

@app.route('/download/<filename>')
def download_file(filename):
    """Serves the generated MP3 file for download."""
    audio_path = os.path.join(temp_dir, filename)
    if os.path.exists(audio_path):
        return send_file(audio_path, as_attachment=True)
    else:
        return jsonify({"success": False, "message": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=False)
