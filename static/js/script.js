function uploadFile() {
    const fileInput = document.getElementById('pdfUpload');
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('pdf', file);

    fetch('/upload', {
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
    .catch(error => console.error('Error:', error));
}
