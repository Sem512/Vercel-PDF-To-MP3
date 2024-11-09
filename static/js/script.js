// Handles PDF file upload and sends it to backend for parsing
function uploadFile() {
    const pdfFile = document.getElementById('pdfUpload').files[0];

    if (!pdfFile) {
        document.getElementById('outputMessage').innerText = 'Please select a PDF file.';
        return;
    }

    document.getElementById('outputMessage').innerText = 'Uploading...';

    // Create a new FormData object
    const formData = new FormData();
    formData.append('pdf', pdfFile);

    // Send the file to the backend (app.py) for parsing
    fetch('/parse-pdf', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.text) {
            document.getElementById('outputMessage').innerText = 'Text extracted. Sending to Lambda for conversion...';

            // Call Lambda function to convert text to speech
            convertTextToSpeech(data.text);
        } else {
            document.getElementById('outputMessage').innerText = 'Failed to extract text from PDF.';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('outputMessage').innerText = 'An error occurred while processing the file.';
    });
}

// Function to call the Lambda function to convert text to speech
function convertTextToSpeech(text) {
    const requestBody = {
        text: text,
        filename: 'converted-audio'
    };

    fetch('https://ccvjmdt3th.execute-api.eu-north-1.amazonaws.com/prod/convert-pdf', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
    })
    .then(response => response.json())
    .then(data => {
        if (data.audio_url) {
            const downloadLink = document.createElement('a');
            downloadLink.href = data.audio_url;
            downloadLink.download = 'output.mp3';
            downloadLink.innerText = 'Download your audiobook';
            document.getElementById('outputMessage').innerText = 'Conversion successful!';
            document.getElementById('outputMessage').appendChild(downloadLink);
        } else {
            document.getElementById('outputMessage').innerText = 'Failed to convert text to speech.';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('outputMessage').innerText = 'An error occurred while converting text to speech.';
    });
}
