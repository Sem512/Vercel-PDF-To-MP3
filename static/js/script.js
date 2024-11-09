function uploadFile() {
    const pdfFile = document.getElementById('pdfUpload').files[0];

    if (!pdfFile) {
        document.getElementById('outputMessage').innerText = 'Please select a PDF file.';
        return;
    }

    document.getElementById('outputMessage').innerText = 'Uploading...';
    document.getElementById('progressContainer').style.display = 'block';
    document.getElementById('progressBar').value = 0;
    document.getElementById('progressText').innerText = '0%';

    // Create a new FormData object
    const formData = new FormData();
    formData.append('pdf', pdfFile);

    // Create a new XMLHttpRequest to send the PDF file
    const xhr = new XMLHttpRequest();
    
    // Update this URL with your Flask backend URL
    xhr.open('POST', 'https://vercel-pdf-to-mp-3-delta.vercel.app/upload', true);  // Replace with your Flask URL

    xhr.responseType = 'json';  // Expecting a JSON response with audio file URL

    xhr.upload.onprogress = function(event) {
        if (event.lengthComputable) {
            const percentComplete = Math.round((event.loaded / event.total) * 100);
            document.getElementById('progressBar').value = percentComplete;
            document.getElementById('progressText').innerText = percentComplete + '%';
        }
    };

    xhr.onload = function() {
        if (xhr.status === 200) {
            // Assuming the response contains a JSON object with a URL to the audio file
            const response = xhr.response;
            if (response.success) {
                const audioUrl = response.audio_files[0];  // Adjust based on the backend response

                // Create a download link for the audio file
                const downloadLink = document.createElement('a');
                downloadLink.href = audioUrl;  // The S3 URL or generated URL for downloading
                downloadLink.download = 'output.mp3';  // Default filename
                downloadLink.innerText = 'Download your audiobook';
                downloadLink.style.display = 'block';

                document.getElementById('outputMessage').innerText = 'Conversion successful!';
                document.getElementById('outputMessage').appendChild(downloadLink);
            } else {
                document.getElementById('outputMessage').innerText = 'Conversion failed. Please try again.';
            }
        } else {
            document.getElementById('outputMessage').innerText = 'Conversion failed. Please try again.';
        }
        
        // Reset progress bar
        document.getElementById('progressBar').value = 0;
        document.getElementById('progressContainer').style.display = 'none';
    };

    xhr.onerror = function() {
        document.getElementById('outputMessage').innerText = 'An error occurred. Please try again later.';
        document.getElementById('progressContainer').style.display = 'none';
    };

    // Send the FormData with the PDF file
    xhr.send(formData);
}
