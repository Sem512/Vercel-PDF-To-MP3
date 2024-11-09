async function uploadFile() {
    const fileInput = document.getElementById('pdfUpload');
    const file = fileInput.files[0];

    if (!file) {
        document.getElementById('outputMessage').textContent = 'Please select a PDF file.';
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    // Assuming the backend API is accessible at /extract-text
    const response = await fetch('/extract-text', {  // Adjust this endpoint as needed
        method: 'POST',
        body: formData
    });

    if (response.ok) {
        const { extractedText } = await response.json();
        
        // Now we send the text to Lambda
        const lambdaResponse = await fetch('https://ccvjmdt3th.execute-api.eu-north-1.amazonaws.com/prod/convert-pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: extractedText,
                filename: file.name.replace('.pdf', '')  // Clean filename for S3
            })
        });

        if (lambdaResponse.ok) {
            const result = await lambdaResponse.json();
            document.getElementById('outputMessage').textContent = `Audio URL: ${result.audio_url}`;
        } else {
            document.getElementById('outputMessage').textContent = 'Error converting text to audio.';
        }
    } else {
        document.getElementById('outputMessage').textContent = 'Error extracting text from PDF.';
    }
}