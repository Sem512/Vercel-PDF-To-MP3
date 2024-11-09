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
    
    // Update this URL with your Lambda API Gateway URL
    xhr.open('POST', 'https://ccvjmdt3th.execute-api.eu-north-1.amazonaws.com/prod/convert-pdf', true);  // Replace with your API Gateway URL

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
            const audioUrl = response.audio_url;  // Adjust based on how the Lambda function returns the audio file URL

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
