function uploadFile() {
    const fileInput = document.getElementById('pdfUpload');
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('pdf', file);

    // Send the file to Flask endpoint for text extraction
    fetch('https://vercel-pdf-to-mp-3-delta.vercel.app/upload', {  // Replace with your Flask URL
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        // Log response from Flask (which includes extracted text and logs)
        console.log("Flask Response: ", data);

        if (data.success) {
            // Send the extracted text to Lambda for conversion to MP3
            sendToLambda(data.extracted_text, data.filename);
        } else {
            document.getElementById('outputMessage').textContent = data.message || 'An error occurred during PDF processing.';
        }
    })
    .catch(error => {
        console.error('Error during PDF upload:', error);
        document.getElementById('outputMessage').textContent = 'An error occurred during the upload.';
    });
}

function sendToLambda(extractedText, filename) {
    const lambdaRequestBody = JSON.stringify({
        text: extractedText,
        filename: filename
    });

    // Send extracted text to Lambda function for MP3 conversion
    fetch('https://ccvjmdt3th.execute-api.eu-north-1.amazonaws.com/prod/convert-pdf', {  // Replace with your Lambda URL
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: lambdaRequestBody
    })
    .then(response => response.json())
    .then(data => {
        // Log Lambda response (includes MP3 URL and logs)
        console.log("Lambda Response: ", data);

        if (data.audio_url) {
            // Display the MP3 URL for download
            document.getElementById('outputMessage').innerHTML = `<a href="${data.audio_url}" download>Download Audio</a>`;
        }

        if (data.logs && data.logs.length > 0) {
            // Optionally, log the Lambda logs to console or UI
            data.logs.forEach(log => {
                console.log(log);  // Print logs to the console
            });
        }

    })
    .catch(error => {
        console.error('Error during MP3 conversion:', error);
        document.getElementById('outputMessage').textContent = 'An error occurred during the MP3 conversion.';
    });
}
