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
    formData.append('pdf', pdfFile); // Append the PDF file

    const xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://127.0.0.1:5000/upload', true); // Open the request

    xhr.upload.onprogress = function(event) {
        if (event.lengthComputable) {
            const percentComplete = Math.round((event.loaded / event.total) * 100);
            document.getElementById('progressBar').value = percentComplete;
            document.getElementById('progressText').innerText = percentComplete + '%';
        }
    };

    xhr.onload = function() {
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            if (response.success) {
                document.getElementById('outputMessage').innerText = 'Conversion successful! Download your audiobook below.';
                displayDownloadLink(response.audio_url);
            } else {
                document.getElementById('outputMessage').innerText = response.message || 'Conversion failed. Please try again.';
            }
        } else {
            document.getElementById('outputMessage').innerText = 'Upload failed. Please try again.';
        }
        document.getElementById('progressBar').value = 0; // Reset progress bar
        document.getElementById('progressContainer').style.display = 'none';
    };

    xhr.onerror = function() {
        document.getElementById('outputMessage').innerText = 'An error occurred. Please try again later.';
        document.getElementById('progressContainer').style.display = 'none';
    };

    // Send the FormData object
    console.log([...formData]);
    xhr.send(formData);
}


function displayDownloadLink(url) {
    const outputMessage = document.getElementById('outputMessage');
    outputMessage.innerHTML = ''; // Clear previous messages
    const downloadLink = document.createElement('a');
    downloadLink.href = url;
    downloadLink.innerText = 'Download your audiobook';
    downloadLink.download = '';
    outputMessage.appendChild(document.createElement('br'));
    outputMessage.appendChild(downloadLink);
}
