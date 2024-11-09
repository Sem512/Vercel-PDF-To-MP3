function uploadFile() {
    const fileInput = document.getElementById('pdfUpload');
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('pdf', file);

    // Change this to your Flask endpoint where app.py is handling the file upload
    fetch('https://127.0.0.1:5000/upload', {  // Replace with your Flask URL
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('outputMessage').innerHTML = `<a href="${data.audio_url}" download>Download Audio</a>`;
        } else {
            document.getElementById('outputMessage').textContent = data.message;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('outputMessage').textContent = 'An error occurred during the upload.';
    });
}
