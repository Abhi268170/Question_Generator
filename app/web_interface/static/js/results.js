// Results page JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // View toggle functionality
    const listViewBtn = document.getElementById('list-view-btn');
    const carouselViewBtn = document.getElementById('carousel-view-btn');
    const listView = document.getElementById('list-view');
    const carouselView = document.getElementById('carousel-view');
    const carouselCounter = document.getElementById('carousel-counter');
    
    // Initialize the carousel
    const carousel = new bootstrap.Carousel(document.getElementById('questionCarousel'), {
        interval: false,
        wrap: true
    });
    
    // Switch to list view
    listViewBtn.addEventListener('click', function() {
        listView.style.display = 'block';
        carouselView.style.display = 'none';
        listViewBtn.classList.add('active');
        carouselViewBtn.classList.remove('active');
        
        // Save preference to localStorage
        localStorage.setItem('preferredView', 'list');
    });
    
    // Switch to carousel view
    carouselViewBtn.addEventListener('click', function() {
        listView.style.display = 'none';
        carouselView.style.display = 'block';
        listViewBtn.classList.remove('active');
        carouselViewBtn.classList.add('active');
        
        // Save preference to localStorage
        localStorage.setItem('preferredView', 'carousel');
    });
    
    // Update carousel counter when slide changes
    const questionCarousel = document.getElementById('questionCarousel');
    if (questionCarousel) {
        questionCarousel.addEventListener('slide.bs.carousel', function(event) {
            const totalQuestions = document.querySelectorAll('.carousel-item').length;
            const currentIndex = event.to + 1;
            carouselCounter.textContent = `Question ${currentIndex} of ${totalQuestions}`;
        });
    }
    
    // Check if user has a saved preference
    const preferredView = localStorage.getItem('preferredView');
    if (preferredView === 'carousel') {
        carouselViewBtn.click();
    }
    
    // Download JSON functionality
    const downloadBtn = document.getElementById('download-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            // Get the data from the page
            const questionsData = JSON.parse(document.getElementById('questions-data').textContent);
            
            // Create a Blob with the data
            const blob = new Blob([JSON.stringify(questionsData, null, 2)], { type: 'application/json' });
            
            // Create a download link
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'generated_questions.json';
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            setTimeout(function() {
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            }, 0);
        });
    }
    
    // Keyboard navigation for carousel
    document.addEventListener('keydown', function(event) {
        // Only if carousel view is active
        if (carouselView.style.display === 'block') {
            if (event.key === 'ArrowLeft') {
                carousel.prev();
            } else if (event.key === 'ArrowRight') {
                carousel.next();
            }
        }
    });
});
