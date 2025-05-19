/**
 * GlaCK0N GarageHub - Vehicle Filter System
 * This file handles the vehicle filtering functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize vehicle filter if the form exists
    const filterForm = document.getElementById('vehicleFilterForm');
    if (filterForm) {
        initializeVehicleFilter();
    }
});

/**
 * Initialize the vehicle filter functionality
 */
function initializeVehicleFilter() {
    // Get form elements
    const makeSelect = document.getElementById('makeSelect');
    const modelSelect = document.getElementById('modelSelect');
    const vehicleCountElement = document.getElementById('vehicleCount');
    
    // Add event listener to make select to update models
    if (makeSelect) {
        makeSelect.addEventListener('change', function() {
            updateModels(makeSelect.value, modelSelect);
        });
    }
    
    // Initialize models if make is already selected
    if (makeSelect && makeSelect.value && makeSelect.value !== '0') {
        updateModels(makeSelect.value, modelSelect);
    }
    
    // Add listeners to filter inputs for live filtering
    setupLiveFiltering();
}

/**
 * Update models dropdown based on selected make
 * @param {string} makeId 
 * @param {HTMLSelectElement} modelSelect 
 */
function updateModels(makeId, modelSelect) {
    if (!modelSelect) return;
    
    // If "All Makes" is selected
    if (makeId === '0' || makeId === '') {
        // Clear models and add placeholder
        modelSelect.innerHTML = '<option value="0">All Models</option>';
        return;
    }
    
    // Show loading state
    modelSelect.innerHTML = '<option value="">Loading...</option>';
    
    // Fetch models for selected make
    fetch(`/api/models/${makeId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Clear the select
            modelSelect.innerHTML = '';
            
            // Add "All Models" option
            const allOption = document.createElement('option');
            allOption.value = '0';
            allOption.textContent = 'All Models';
            modelSelect.appendChild(allOption);
            
            // Add model options
            data.forEach(model => {
                const option = document.createElement('option');
                option.value = model.id;
                option.textContent = model.name;
                modelSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching models:', error);
            modelSelect.innerHTML = '<option value="0">Error loading models</option>';
        });
}

/**
 * Set up live filtering for the vehicle list
 */
function setupLiveFiltering() {
    // Get all filter inputs
    const filterInputs = document.querySelectorAll('#vehicleFilterForm select, #vehicleFilterForm input');
    
    // Get the form and prevent default submission
    const filterForm = document.getElementById('vehicleFilterForm');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            applyFilters();
        });
    }
    
    // Add change event listeners to inputs for immediate filtering
    filterInputs.forEach(input => {
        // For selects, apply on change
        if (input.tagName === 'SELECT') {
            input.addEventListener('change', function() {
                // If it's the make select, don't filter immediately (wait for models to load)
                if (input.id !== 'makeSelect') {
                    applyFilters();
                }
            });
        }
        
        // For text/number inputs, apply on debounced input
        if (input.tagName === 'INPUT' && (input.type === 'text' || input.type === 'number')) {
            input.addEventListener('input', debounce(function() {
                applyFilters();
            }, 500));
        }
    });
}

/**
 * Apply filters and update the vehicle list
 */
function applyFilters() {
    // Get form data
    const filterForm = document.getElementById('vehicleFilterForm');
    const formData = new FormData(filterForm);
    
    // Build query string
    const params = new URLSearchParams();
    for (const [key, value] of formData.entries()) {
        if (value) { // Only add if value is not empty
            params.append(key, value);
        }
    }
    
    // Navigate to the filtered URL
    window.location.href = `${window.location.pathname}?${params.toString()}`;
}

/**
 * Debounce function to limit how often a function can be called
 * @param {Function} func 
 * @param {number} wait 
 * @returns {Function}
 */
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}
