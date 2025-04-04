// Processing page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const progressBar = document.getElementById('progress-bar');
    const statusMessage = document.getElementById('status-message');
    const errorContainer = document.getElementById('error-container');
    
    // Simulate progress
    let progress = 0;
    const interval = setInterval(function() {
        progress += 5;
        if (progress <= 90) {
            progressBar.style.width = progress + '%';
            
            // Update status message based on progress
            if (progress < 20) {
                statusMessage.textContent = 'Analyzing PDF document...';
            } else if (progress < 40) {
                statusMessage.textContent = 'Processing text chunks...';
            } else if (progress < 60) {
                statusMessage.textContent = 'Retrieving relevant content...';
            } else if (progress < 80) {
                statusMessage.textContent = 'Generating questions...';
            } else {
                statusMessage.textContent = 'Finalizing results...';
            }
        }
    }, 300);
    
    // Start question generation
    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        clearInterval(interval);
        
        if (data.error) {
            // Show error
            errorContainer.textContent = 'Error: ' + data.error;
            errorContainer.style.display = 'block';
            progressBar.classList.remove('progress-bar-animated');
            progressBar.classList.add('bg-danger');
            statusMessage.textContent = 'Failed to generate questions';
        } else if (data.redirect) {
            // Redirect to results page
            progressBar.style.width = '100%';
            statusMessage.textContent = 'Questions generated successfully!';
            setTimeout(function() {
                window.location.href = data.redirect;
            }, 500);
        }
    })
    .catch(error => {
        clearInterval(interval);
        errorContainer.textContent = 'Error: ' + error.message;
        errorContainer.style.display = 'block';
        progressBar.classList.remove('progress-bar-animated');
        progressBar.classList.add('bg-danger');
        statusMessage.textContent = 'Failed to generate questions';
    });
});
