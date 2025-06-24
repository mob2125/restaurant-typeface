
// static/js/script.js

// --- ELEMENT REFERENCES ---
const restaurantListDiv = document.getElementById('restaurant-list');
const paginationDiv = document.getElementById('pagination-controls');
const loadingDiv = document.getElementById('loading');
const textSearchForm = document.getElementById('text-search-form');
const textSearchInput = document.getElementById('text-search-input');
const categoryGrid = document.getElementById('category-grid');
const resultsHeader = document.getElementById('results-header');
const filterForm = document.getElementById('filter-form');
const countrySelect = document.getElementById('country-select');
const maxCostInput = document.getElementById('max-cost-input');
const cuisineInput = document.getElementById('cuisine-input');
const clearFiltersBtn = document.getElementById('clear-filters-btn');
const geoSearchForm = document.getElementById('geo-search-form');
const imageSearchForm = document.getElementById('image-search-form');
const toggleFiltersBtn = document.getElementById('toggle-filters-btn');
const advancedSearchPanel = document.getElementById('advanced-search-panel');

// --- DATA & CONFIG ---
const cuisineImages = {
    'Pizza': 'https://images.unsplash.com/photo-1593560708920-61dd98c46a4e?w=400',
    'Chinese': 'https://images.unsplash.com/photo-1585851373321-39e55145b2be?w=400',
    'Italian': 'https://images.unsplash.com/photo-1533777857889-45b70161c248?w=400',
    'North Indian': 'https://images.unsplash.com/photo-1606495147382-7246236d1e3e?w=400',
    'Cafe': 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400',
    'Bakery': 'https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=400',
    'Desserts': 'https://images.unsplash.com/photo-1551024601-bec78c944514?w=400',
    'American': 'https://images.unsplash.com/photo-1561758033-d89a9ad46330?w=400',
    'Burger': 'https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=400',
    'Sandwich': 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400',
    'Default': 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400'
};
const categoryData = [
    { name: 'Pizza', image: cuisineImages['Pizza'] }, { name: 'Cafe', image: cuisineImages['Cafe'] },
    { name: 'Chinese', image: cuisineImages['Chinese'] }, { name: 'North Indian', image: cuisineImages['North Indian'] },
    { name: 'Bakery', image: cuisineImages['Bakery'] }, { name: 'Desserts', image: cuisineImages['Desserts'] }
];

// --- STATE MANAGEMENT FOR CLIENT-SIDE PAGINATION ---
let clientSideResultSet = []; // This will only hold results for geo and image search
const ITEMS_PER_PAGE = 6;

// --- CORE FUNCTIONS ---

// Function for default list and advanced text filters (SERVER-SIDE pagination)
function loadFilteredRestaurants(page = 1) {
    loadingDiv.style.display = 'block';
    restaurantListDiv.innerHTML = '';
    paginationDiv.innerHTML = '';

    let params = new URLSearchParams({ page: page, per_page: ITEMS_PER_PAGE });
    const searchTerm = textSearchInput.value;
    const country = countrySelect.value;
    const maxCost = maxCostInput.value;
    const cuisine = cuisineInput.value;
    
    let headerText = "Featured Restaurants";
    if (searchTerm || country || maxCost || cuisine) {
        if (searchTerm) params.append('search', searchTerm);
        if (country) params.append('country', country);
        if (maxCost) params.append('max_cost', maxCost);
        if (cuisine) params.append('cuisine', cuisine);
        headerText = `Showing Search Results`;
    }
    resultsHeader.innerHTML = `<h2 class="section-title">${headerText}</h2>`;

    fetch(`/api/restaurants?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            loadingDiv.style.display = 'none';
            displayRestaurants(data.data);
            buildPagination(data.pagination, 'loadFilteredRestaurants');
        });
}

// Renders a page of results from the clientSideResultSet
function renderClientSidePage(page = 1) {
    const start = (page - 1) * ITEMS_PER_PAGE;
    const end = start + ITEMS_PER_PAGE;
    const pageItems = clientSideResultSet.slice(start, end);
    
    displayRestaurants(pageItems);
    buildPagination(null, 'renderClientSidePage', clientSideResultSet.length, page);
}

// Generic function to display a list of restaurant cards
function displayRestaurants(restaurants) {
    restaurantListDiv.innerHTML = ''; 
    if (!restaurants || restaurants.length === 0) {
        restaurantListDiv.innerHTML = '<p style="text-align:center; font-size: 1.2rem;">No restaurants found.</p>';
        return;
    }
    restaurants.forEach((restaurant, index) => {
        let imageUrl = cuisineImages['Default'];
        if (restaurant.cuisines) {
            for (const cuisine of Object.keys(cuisineImages)) {
                if (restaurant.cuisines.includes(cuisine)) {
                    imageUrl = cuisineImages[cuisine];
                    break;
                }
            }
        }
        const card = document.createElement('div');
        card.className = 'restaurant-card';
        card.innerHTML = `
            <img src="${imageUrl}" alt="${restaurant.restaurant_name}">
            <div class="card-content">
                <div class="card-header">
                    <h2><a href="/restaurant/${restaurant.restaurant_id}" style="color: inherit; text-decoration: none;">${restaurant.restaurant_name}</a></h2>
                    <div class="rating">${restaurant.aggregate_rating} ★</div>
                </div>
                <div class="card-details-grid">
                    <div class="detail-box">
                        <span>${restaurant.city || 'N/A'}</span>
                    </div>
                    <div class="detail-box cuisines">
                        <span>${restaurant.cuisines || 'Not specified'}</span>
                    </div>
                </div>
            </div>
        `;
        restaurantListDiv.appendChild(card);
        setTimeout(() => { card.classList.add('is-visible'); }, index * 100);
    });
}

// Generic function to build pagination controls
function buildPagination(paginationData, functionToCall, totalItems = 0, currentPage = 1) {
    paginationDiv.innerHTML = '';
    let totalPages;

    if (paginationData) { // Server-side pagination
        totalPages = paginationData.total_pages;
        currentPage = paginationData.current_page;
    } else { // Client-side pagination
        totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE);
    }
    
    if (totalPages <= 1) return;

    const hasPrev = currentPage > 1;
    const hasNext = currentPage < totalPages;

    paginationDiv.innerHTML = `
        ${hasPrev ? `<a onclick="${functionToCall}(${currentPage - 1})">‹ Prev</a>` : `<span class="disabled">‹ Prev</span>`}
        <span class="current-page">${currentPage} of ${totalPages}</span>
        ${hasNext ? `<a onclick="${functionToCall}(${currentPage + 1})">Next ›</a>` : `<span class="disabled">Next ›</span>`}
    `;
}
        
function populateCategories() {
    categoryData.forEach((cat, index) => {
        const item = document.createElement('div');
        item.className = 'category-item fade-in-up';
        item.style.animationDelay = `${index * 100}ms`;
        item.innerHTML = `<img src="${cat.image}" alt="${cat.name}"><span>${cat.name}</span>`;
        item.addEventListener('click', () => { textSearchInput.value = cat.name; loadFilteredRestaurants(1); });
        categoryGrid.appendChild(item);
    });
}

function populateCountries() {
     fetch('/api/countries')
        .then(response => response.json())
        .then(countries => {
            countries.forEach(country => {
                const option = document.createElement('option');
                option.value = country;
                option.textContent = country;
                countrySelect.appendChild(option);
            });
        });
}

// --- EVENT LISTENERS ---
textSearchForm.addEventListener('submit', e => { e.preventDefault(); loadFilteredRestaurants(1); });
filterForm.addEventListener('submit', e => { e.preventDefault(); loadFilteredRestaurants(1); });

geoSearchForm.addEventListener('submit', function(event) {
     event.preventDefault();
     const lat = document.getElementById('lat-input').value;
     const lon = document.getElementById('lon-input').value;
     const radiusKm = document.getElementById('radius-input').value;
     if (!lat || !lon || !radiusKm) return;
     
     const radiusMeters = parseFloat(radiusKm) * 1000;
     const apiUrl = `/api/restaurants/search/nearby?lat=${lat}&lon=${lon}&radius=${radiusMeters}&per_page=9999`; // Get all results
     
     loadingDiv.style.display = 'block';
     restaurantListDiv.innerHTML = '';
     paginationDiv.innerHTML = '';
     resultsHeader.innerHTML = `<h2 class="section-title">Searching Restaurants Near You...</h2>`;
     
     fetch(apiUrl)
         .then(response => response.json())
         .then(data => {
             loadingDiv.style.display = 'none';
             resultsHeader.innerHTML = `<h2 class="section-title">Restaurants Near You</h2>`;
             clientSideResultSet = data.data; // Store the full list
             renderClientSidePage(1); // Render the first page
         });
});

imageSearchForm.addEventListener('submit', function(event) {
    event.preventDefault();
    const imageInput = document.getElementById('image-upload-input');
    const file = imageInput.files[0];
    if (!file) { alert('Please select an image file first.'); return; }
    
    const formData = new FormData();
    formData.append('food_image', file);
    loadingDiv.style.display = 'block';
    restaurantListDiv.innerHTML = '';
    paginationDiv.innerHTML = '';
    resultsHeader.innerHTML = `<h2 class="section-title">Analyzing Image...</h2>`;

    fetch('/api/search/by-image', { method: 'POST', body: formData })
    .then(response => response.json())
    .then(data => {
        loadingDiv.style.display = 'none';
        if (data.error) {
            alert(`Error: ${data.error}`);
            resultsHeader.innerHTML = `<h2 class="section-title">Search Failed</h2>`;
        } else {
            resultsHeader.innerHTML = `<h2 class="section-title">Showing restaurants serving ${data.generalized_food}</h2>`;
            clientSideResultSet = data.data; // Store the full list
            renderClientSidePage(1); // Render the first page
        }
    });
});

clearFiltersBtn.addEventListener('click', function() {
    filterForm.reset();
    textSearchForm.reset();
    geoSearchForm.reset();
    imageSearchForm.reset();
    loadFilteredRestaurants(1);
});

toggleFiltersBtn.addEventListener('click', () => {
    advancedSearchPanel.classList.toggle('is-open');
});

document.addEventListener('DOMContentLoaded', () => {
    populateCountries();
    populateCategories();
    loadFilteredRestaurants(1);
});