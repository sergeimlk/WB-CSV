function showLoader() {
    document.getElementById('loader').style.display = 'block';
}

function hideLoader() {
    document.getElementById('loader').style.display = 'none';
}

document.getElementById('uploadForm').onsubmit = async function (event) {
    event.preventDefault();

    // Show loader
    showLoader();

    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const convertBtn = document.getElementById('convertBtn');
    const downloadBtn = document.getElementById('downloadBtn');

    try {
        const formData = new FormData(this);
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            convertBtn.style.display = 'none';
            downloadBtn.style.display = 'inline-block';
            downloadBtn.onclick = function () {
                window.location.href = `/download/${result.filename}`;
            };
        } else {
            const result = await response.json();
            errorDiv.style.display = 'block';
            errorDiv.textContent = `Error: ${result.error}`;
        }
    } catch (error) {
        errorDiv.style.display = 'block';
        errorDiv.textContent = `Error: ${error.message}`;
    } finally {
        // Hide loader
        hideLoader();
    }
};
