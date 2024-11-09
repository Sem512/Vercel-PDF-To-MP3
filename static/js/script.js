function uploadFile() {
    const pdfFile = document.getElementById('pdfUpload').files[0];
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const outputMessage = document.getElementById('outputMessage');

    if (!pdfFile) {
        alert("Please select a PDF file.");
        return;
    }

    // Show the progress bar
    progressContainer.style.display = 'block';

    const formData = new FormData();
    formData.append('pdf', pdfFile);

    // Disable the upload button to prevent multiple submissions
    const uploadButton = event.target;
    uploadButton.disabled = true;
    uploadButton.textContent = 'Uploading...';

    // Send the PDF to the Flask backend
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        uploadButton.disabled = false;
        uploadButton.textContent = 'Upload & Convert';

        // Hide progress bar after completion
        progressContainer.style.display = 'none';

        if (data.success) {
            // Display the audio download link
            const audioUrl = data.audio_files; // The URL returned from Lambda
            const downloadLink = document.createElement('a');
            downloadLink.href = audioUrl;
            downloadLink.textContent = 'Download Audio';
            downloadLink.download = 'converted_audio.mp3'; // Set a default name for the download
            outputMessage.innerHTML = ''; // Clear the previous message
            outputMessage.appendChild(downloadLink);
        } else {
            outputMessage.textContent = `Error: ${data.message}`;
        }
    })
    .catch(error => {
        uploadButton.disabled = false;
        uploadButton.textContent = 'Upload & Convert';
        progressContainer.style.display = 'none';
        outputMessage.textContent = `An error occurred: ${error}`;
    });
}
