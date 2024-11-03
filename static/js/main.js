// Main JavaScript file
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any JavaScript functionality
    
    // Example: Handle property search form
    const searchForm = document.querySelector('form[action="/properties"]');
    if (searchForm) {
        searchForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(searchForm);
            const params = new URLSearchParams(formData);
            
            try {
                const response = await fetch(`/api/properties?${params}`);
                const data = await response.json();
                // Handle the response data
                console.log(data);
            } catch (error) {
                console.error('Error:', error);
            }
        });
    }
});