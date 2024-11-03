// Map initialization and functionality
let map;
let markers = [];
const cities = {
    toronto: { lat: 43.6532, lng: -79.3832 },
    vancouver: { lat: 49.2827, lng: -123.1207 },
    ottawa: { lat: 45.4215, lng: -75.6972 }
};

function initMap(city = 'toronto') {
    map = L.map('map').setView(cities[city], 12);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // Initialize search controls
    initSearchControls();
    
    // Load initial properties
    loadProperties();
}

function initSearchControls() {
    const citySelect = document.getElementById('citySelect');
    const propertyTypeSelect = document.getElementById('propertyTypeSelect');
    const priceRange = document.getElementById('priceRange');
    
    citySelect.addEventListener('change', () => {
        map.setView(cities[citySelect.value], 12);
        loadProperties();
    });
    
    propertyTypeSelect.addEventListener('change', loadProperties);
    priceRange.addEventListener('input', updatePriceLabel);
    priceRange.addEventListener('change', loadProperties);
}

function updatePriceLabel() {
    const priceRange = document.getElementById('priceRange');
    const priceLabel = document.getElementById('priceLabel');
    priceLabel.textContent = `$${parseInt(priceRange.value).toLocaleString()}`;
}

async function loadProperties() {
    const citySelect = document.getElementById('citySelect');
    const propertyTypeSelect = document.getElementById('propertyTypeSelect');
    const priceRange = document.getElementById('priceRange');
    
    const params = new URLSearchParams({
        city: citySelect.value,
        type: propertyTypeSelect.value,
        maxPrice: priceRange.value
    });
    
    try {
        const response = await fetch(`/api/properties?${params}`);
        const properties = await response.json();
        
        // Clear existing markers
        markers.forEach(marker => marker.remove());
        markers = [];
        
        // Add new markers
        properties.forEach(property => {
            const marker = L.marker([property.latitude, property.longitude])
                .bindPopup(createPropertyPopup(property))
                .addTo(map);
            markers.push(marker);
        });
        
        // Update property list
        updatePropertyList(properties);
    } catch (error) {
        console.error('Error loading properties:', error);
    }
}

function createPropertyPopup(property) {
    return `
        <div class="property-popup">
            <h3>${property.address}</h3>
            <p class="price">$${property.price.toLocaleString()}</p>
            <p>${property.bedrooms} beds • ${property.bathrooms} baths</p>
            <p>${property.square_feet.toLocaleString()} sq ft</p>
            <button onclick="showPropertyDetails('${property.id}')" class="view-details">
                View Details
            </button>
        </div>
    `;
}

function updatePropertyList(properties) {
    const propertyList = document.getElementById('propertyList');
    propertyList.innerHTML = properties.map(property => `
        <div class="property-card">
            <div class="property-card-content">
                <h3>${property.address}</h3>
                <p class="price">$${property.price.toLocaleString()}</p>
                <p>${property.bedrooms} beds • ${property.bathrooms} baths</p>
                <p>${property.square_feet.toLocaleString()} sq ft</p>
                <button onclick="showPropertyDetails('${property.id}')" class="view-details">
                    View Details
                </button>
            </div>
        </div>
    `).join('');
}

async function showPropertyDetails(propertyId) {
    try {
        const response = await fetch(`/api/properties/${propertyId}`);
        const property = await response.json();
        
        // Show property details modal
        const modal = document.getElementById('propertyModal');
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close">&times;</span>
                <h2>${property.address}</h2>
                <div class="property-details">
                    <p class="price">$${property.price.toLocaleString()}</p>
                    <div class="details-grid">
                        <div>
                            <h4>Property Details</h4>
                            <p>${property.bedrooms} bedrooms</p>
                            <p>${property.bathrooms} bathrooms</p>
                            <p>${property.square_feet.toLocaleString()} sq ft</p>
                            <p>Built in ${property.year_built}</p>
                        </div>
                        <div>
                            <h4>Location Info</h4>
                            <p>${property.neighborhood}</p>
                            <p>${property.city}</p>
                            <p>Walk Score: ${property.walk_score}</p>
                        </div>
                    </div>
                    <button onclick="requestViewing('${property.id}')" class="request-viewing">
                        Request Viewing
                    </button>
                </div>
            </div>
        `;
        
        modal.style.display = 'block';
        
        // Close modal functionality
        const closeBtn = modal.querySelector('.close');
        closeBtn.onclick = () => modal.style.display = 'none';
        window.onclick = (event) => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        };
    } catch (error) {
        console.error('Error loading property details:', error);
    }
}

async function requestViewing(propertyId) {
    // Implement viewing request functionality
    alert('Viewing request feature coming soon!');
}