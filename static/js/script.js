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
    xhr.open('POST', 'https://vercel-pdf-to-mp-3-delta.vercel.app/upload', true);  // Replace with your Vercel URL

    xhr.responseType = 'blob'; // Set the response type to blob to handle the audio file download

    xhr.upload.onprogress = function(event) {
        if (event.lengthComputable) {
            const percentComplete = Math.round((event.loaded / event.total) * 100);
            document.getElementById('progressBar').value = percentComplete;
            document.getElementById('progressText').innerText = percentComplete + '%';
        }
    };

    xhr.onload = function() {
        if (xhr.status === 200) {
            // Handle the blob response (audio file)
            const audioBlob = xhr.response;
            const downloadUrl = window.URL.createObjectURL(audioBlob);

            // Create a download link for the audio file
            const downloadLink = document.createElement('a');
            downloadLink.href = downloadUrl;
            downloadLink.download = 'output.mp3'; // Set a default filename for download
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
