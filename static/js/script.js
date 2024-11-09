function uploadFile() {
    const fileInput = document.getElementById('pdfUpload');
    const file = fileInput.files[0];
    
    // Create a FormData object to upload the file to Flask
    const formData = new FormData();
    formData.append('pdf', file);

    // Send the file to the Flask server first
    fetch('/upload', {  // Ensure this is the correct endpoint on your Flask app
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // If the file was processed and audio URL is returned
            const text = data.extracted_text;  // Ensure this is being sent by Flask in response
            const filename = file.name;

            // Now, send the text to Lambda for MP3 conversion
            return fetch('https://ccvjmdt3th.execute-api.eu-north-1.amazonaws.com/prod/convert-pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    filename: filename
                })
            });
        } else {
            document.getElementById('outputMessage').textContent = data.message;
            throw new Error(data.message);
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.audio_url) {
            // If Lambda returns a valid audio URL, display it
            document.getElementById('outputMessage').innerHTML = `<a href="${data.audio_url}" download>Download Audio</a>`;
        } else {
            throw new Error('No audio URL returned by Lambda');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('outputMessage').textContent = 'An error occurred during the upload or conversion.';
    });
}
