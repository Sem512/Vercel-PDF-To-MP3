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

    // Create a new FormData object for the PDF file (if needed)
    const formData = new FormData();
    formData.append('pdf', pdfFile);

    // Log the FormData to ensure it's correct
    console.log('FormData:', formData);

    // Create the JSON object that will be sent
    const requestBody = {
        text: "Your extracted text from PDF here",
        filename: pdfFile.name
    };

    // Log the JSON object to ensure it's correct
    console.log('Request Body:', JSON.stringify(requestBody));

    // Create an XMLHttpRequest to send the data
    const xhr = new XMLHttpRequest();

    // Specify the API Gateway URL
    xhr.open('POST', 'https://ccvjmdt3th.execute-api.eu-north-1.amazonaws.com/prod/convert-pdf', true);  // Replace with your API Gateway URL

    // Set the correct header to send JSON
    xhr.setRequestHeader('Content-Type', 'application/json');

    // Monitor the upload progress
    xhr.upload.onprogress = function(event) {
        if (event.lengthComputable) {
            const percentComplete = Math.round((event.loaded / event.total) * 100);
            document.getElementById('progressBar').value = percentComplete;
            document.getElementById('progressText').innerText = percentComplete + '%';
        }
    };

    // Handle the response from the server
    xhr.onload = function() {
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText); // Parse the JSON response
            console.log('Response:', response);

            const audioUrl = response.audio_url;  // Assuming response contains the audio URL

            // Create a download link for the audio file
            const downloadLink = document.createElement('a');
            downloadLink.href = audioUrl;  // The S3 URL or generated URL for downloading
            downloadLink.download = 'output.mp3';  // Default filename
            downloadLink.innerText = 'Download your audiobook';
            downloadLink.style.display = 'block';

            // Display success message and append the download link
            document.getElementById('outputMessage').innerText = 'Conversion successful!';
            document.getElementById('outputMessage').appendChild(downloadLink);
        } else {
            document.getElementById('outputMessage').innerText = 'Conversion failed. Please try again.';
        }

        // Reset progress bar
        document.getElementById('progressBar').value = 0;
        document.getElementById('progressContainer').style.display = 'none';
    };

    // Handle errors
    xhr.onerror = function() {
        document.getElementById('outputMessage').innerText = 'An error occurred. Please try again later.';
        document.getElementById('progressContainer').style.display = 'none';
    };

    // Send the JSON object as a string
    xhr.send(JSON.stringify(requestBody));
}
